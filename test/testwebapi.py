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
        return "http://localhost:8118"

    def setUp(self):
        self._server = Server()
        self._web_api = WebApi(self._server)
        self._server.start()
        self._web_api.start()
        while not self._web_api.ready():time.sleep(0.5)

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

    def _encode_dict(self, dict):   # dict --> UTF-8 string
        dict_str = json.dumps(dict)
        dict_encoded = bytearray(source=dict_str, encoding="utf-8")
        return dict_encoded

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

    def test_command_smtp_settings(self):
        smtp_settings = {"host": "smtp.myhost.com", "port": 587, "user": "Moatl", "pwd": "geheim123"}
        smtp_settings_encoded = self._encode_dict(smtp_settings)
        self._api_call("/api/settings/smtp", "PUT", smtp_settings_encoded)
        self.assertDictEqual( self._server.settings["smtp"], smtp_settings)

    def test_command_create_observer(self):
        observer_data = dict(profile="Willhaben",
                             url="that wont work for sure",
                             store=False,
                             interval=30,
                             criteria=[
                                 dict(tag="title",
                                      type="keywords_all",
                                      keywords=["word", "perfect"])])
        observer_data_encoded = self._encode_dict(observer_data)
        self._api_call("/api/observer/MyObserver", "PUT", observer_data_encoded)
        self.assertTrue("MyObserver" in self._server.observers())   # Check if the observer is there
        observer_serialized = self._server["MyObserver"].serialize()    # Check if the server has all the correct properties
        observer_data["name"] = observer_serialized["name"]     # not in the original data
        self.assertDictEqual(observer_data, observer_serialized)

    def test_command_add_notification(self):
        observer = MockObserver("MyObserver")
        self._server.add_observer(observer)
        smtp_settings = {"host": "fake", "port": 0,
                         "user": "me", "pwd": "secret"} # Fake SMTP settings
        self._server.settings["smtp"] = smtp_settings
        notification_data = {"type": "email",
                             "from": "UpdateJunkie <junkie@koloman.net>",
                             "to": [ "Martin Hammerschmied <gestatten@gmail.com>" ],
                             "mime_type": "text/html",
                             "subject": "{title} for {price}",
                             "body": "I found a new ad ({datetime}):<br/><br/>\n<b>{title}</b><br/>\nfor € <b>{price}</b><br/><br/>\n<a href=\"{url}\">{url}</a><br/><br/>\nbye!"
        }
        notification_data_encoded = self._encode_dict(notification_data)
        self._api_call("/api/observer/MyObserver/notification", "POST", notification_data_encoded)
        notification = next(iter(observer.notifications))
        self.assertEqual(notification.host, smtp_settings["host"])
        self.assertEqual(notification.port, smtp_settings["port"])
        self.assertEqual(notification.user, smtp_settings["user"])
        self.assertEqual(notification.pw, smtp_settings["pwd"])

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