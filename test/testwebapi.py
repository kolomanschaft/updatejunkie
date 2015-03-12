#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2012 Martin Hammerschmied

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import unittest
import time
import urllib.request
import urllib.error
import json

from api.webapi import WebApi
from server import Server
from observer import Observer
from notificationserver import NotificationServer

class TestWebApi(unittest.TestCase):

    @property
    def _base_url(self):
        return "http://localhost:8457"

    def setUp(self):
        self._server = Server()
        self._web_api = WebApi(self._server, port=8457)
        self._server.start()
        self._web_api.start()
        self._web_api.wait_ready()

    def tearDown(self):
        self._web_api.quit()
        self._server.quit()
        self._web_api.join()
        self._server.join()

    def _api_call(self, rel_url, method, data=None):
        url = "{}{}".format(self._base_url, rel_url)
        req = urllib.request.Request(url=url, data=data,
                                     headers={'Content-Type': 'application/json'},
                                     method=method)
        with urllib.request.urlopen(req) as f:
            data = None
            json_str = f.read().decode("utf-8")
            if len(json_str) > 0:
                data = json.loads(json_str)
            return data

    def _encode_object(self, object):   # object --> UTF-8 string
        object_str = json.dumps(object)
        object_encoded = object_str.encode('utf-8')
        return object_encoded

    def test_command_list_observers(self):
        # First add 2 mocked observers
        self._server.add_observer(MockObserver("Observer1"))
        self._server.add_observer(MockObserver("Observer2"))

        # Now call the API to see if we get those two
        data = self._api_call("/api/list/observers", "GET")
        self.assertIn("observers", data)
        observer_names = [observer["name"] for observer in data["observers"]]
        self.assertListEqual(observer_names, ["Observer1", "Observer2"])

    def test_command_get_observer(self):
        self._server.add_observer(MockObserver("Observer1"))
        data = self._api_call("/api/observer/Observer1", "GET")
        self.assertDictEqual(data, {"name": "Observer1"})

    def test_command_set_config(self):
        smtp_settings = {"smtp": {"host": "smtp.myhost.com", "port": 587, "auth": True,
                                  "user": "Moatl", "pwd": "geheim123"}}
        # Set all SMTP settings together
        self._api_call("/api/config", "PUT", self._encode_object(smtp_settings))
        self.assertDictEqual(self._server.config.smtp, smtp_settings["smtp"])
        # Set a single string value
        self._api_call("/api/config/smtp/host", "PUT", self._encode_object("say.what.host"))
        self.assertEqual(self._server.config.smtp.host, "say.what.host")
        # Set a single integer value
        self._api_call("/api/config/smtp/port", "PUT", self._encode_object(8123))
        self.assertEqual(self._server.config.smtp.port, 8123)

    def test_command_get_config(self):
        smtp_settings = {"host": "smtp.myhost.com", "port": 587, "auth": True,
                         "user": "Moatl", "pwd": "geheim123"}
        self._server.config.smtp = smtp_settings;
        response_data = self._api_call("/api/config/smtp", "GET")
        self.assertDictEqual(response_data["smtp"], smtp_settings)
        response_data = self._api_call("/api/config/smtp/host", "GET")
        self.assertEqual(response_data["host"], smtp_settings["host"])
        response_data = self._api_call("/api/config/smtp/port", "GET")
        self.assertEqual(response_data["port"], smtp_settings["port"])
        response_data = self._api_call("/api/config", "GET")
        self.assertIn("web", response_data)
        self.assertIn("smtp", response_data)

    def test_command_create_observer(self):
        observer_data = dict(profile="Willhaben",
                             url="that wont work for sure",
                             store=False,
                             interval=30,
                             criteria=[
                                 dict(tag="title",
                                      type="keywords_all",
                                      keywords=["word", "perfect"])])
        observer_data_encoded = self._encode_object(observer_data)
        self._api_call("/api/observer/MyObserver", "PUT", observer_data_encoded)
        self.assertTrue("MyObserver" in self._server.observers())   # Check if the observer is there
        observer_serialized = self._server["MyObserver"].serialize()    # Check if the server has all the correct properties
        observer_data["name"] = observer_serialized["name"]     # not in the original data
        self.assertDictEqual(observer_data, observer_serialized)

    def test_command_add_notification(self):
        observer = MockObserver("MyObserver")
        self._server.add_observer(observer)
        smtp_settings = {"host": "fake", "port": 0, "auth": True,
                         "user": "me", "pwd": "secret"} # Fake SMTP settings
        self._server.config.smtp = smtp_settings
        notification_data = {"type": "email",
                             "from": "UpdateJunkie <junkie@koloman.net>",
                             "to": [ "Martin Hammerschmied <gestatten@gmail.com>" ],
                             "mime_type": "text/html",
                             "subject": "{title} for {price}",
                             "body": "I found a new ad ({datetime}):<br/><br/>\n<b>{title}</b><br/>\nfor € <b>{price}</b><br/><br/>\n<a href=\"{url}\">{url}</a><br/><br/>\nbye!"
        }
        notification_data_encoded = self._encode_object(notification_data)
        self._api_call("/api/observer/MyObserver/notification", "POST", notification_data_encoded)
        notification = next(iter(observer.notifications))
        self.assertEqual(notification._host, smtp_settings["host"])
        self.assertEqual(notification._port, smtp_settings["port"])
        self.assertEqual(notification._user, smtp_settings["user"])
        self.assertEqual(notification._pwd, smtp_settings["pwd"])

    def test_commands_pause_resume_observer(self):
        observer = MockObserver("MyObserver")
        self._server.add_observer(observer)
        observer.state = Observer.RUNNING
        self._api_call("/api/observer/MyObserver/pause", "PUT")
        self.assertEqual(observer.state, Observer.PAUSED)
        self._api_call("/api/observer/MyObserver/resume", "PUT")
        self.assertEqual(observer.state, Observer.RUNNING)

    def test_command_observer_state(self):
        observer = MockObserver("MyObserver")
        self._server.add_observer(observer)
        observer.state = Observer.RUNNING
        data = self._api_call("/api/observer/MyObserver/state", "GET")
        self.assertDictEqual(data, {"state": "RUNNING"})
        observer.state = Observer.PAUSED
        data = self._api_call("/api/observer/MyObserver/state", "GET")
        self.assertDictEqual(data, {"state": "PAUSED"})

    def test_command_remove_observer(self):
        observer = MockObserver("MyObserver")
        self._server.add_observer(observer)
        self.assertIsInstance(self._server["MyObserver"], MockObserver)
        self._api_call("/api/observer/MyObserver", "DELETE")
        self.assertRaises(KeyError, lambda: self._server["MyObserver"])

    def test_command_list_commands(self):
        data = self._api_call("/api/list/commands", "GET")
        self.assertIsInstance(data, dict)
        self.assertIn("commands", data)
        self.assertGreater(len(data["commands"]), 0)
        for cmd in data["commands"]:
            self.assertIsInstance(cmd, str)

    def test_static_route(self):
        import tempfile, os.path
        root = tempfile.gettempdir()
        filepath = tempfile.mktemp()
        file = os.path.basename(filepath)
        content = "This is not the file you are looking for..."
        rel_url = "/showmethefile"
        url = "{}{}/{}".format(self._base_url, rel_url, file)
        with open(filepath, "w") as f:
            f.write(content)
        self._web_api.register_static_directory(root, rel_url)
        with urllib.request.urlopen(url) as f:
            content_get = f.read().decode("utf-8")
        self.assertEqual(content, content_get)


class MockObserver(object):

    def __init__(self, name):
        self._name = name
        self._state = Observer.RUNNING
        self._is_alive = True
        self._notifications = NotificationServer()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def start(self): pass

    def quit(self): self._is_alive = False

    def join(self, timeout): pass

    def is_alive(self): return self._is_alive

    def serialize(self): return {"name": self.name}

    @property
    def notifications(self):
        return self._notifications