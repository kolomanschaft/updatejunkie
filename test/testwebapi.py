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

from api.webapi import WebApi
from server import Server
from observer import Observer

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

    def _api_call(self, rel_url):
        url = "{}{}".format(self._base_url, rel_url)
        with urllib.request.urlopen(url) as f:
            data = eval(f.read())
            return data

    def test_command_list_observers(self):
        # First add 2 mocked observers
        self._server.add_observer(MockObserver("Observer1"))
        self._server.add_observer(MockObserver("Observer2"))

        # Now call the API to see if we get those two
        data = self._api_call("/api/list/observers")
        observer_names = [observer["name"] for observer in data["response"]]
        self.assertListEqual(observer_names, ["Observer1", "Observer2"])

    def test_command_get_observer(self):
        self._server.add_observer(MockObserver("Observer1"))
        data = self._api_call("/api/observer/Observer1")
        self.assertDictEqual(data["response"], {"name": "Observer1"})

class MockObserver(object):

    def __init__(self, name):
        self._name = name
        self._state = Observer.RUNNING
        self._is_alive = True

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def start(self): pass

    def quit(self): self._is_alive = False

    def join(self, timeout): pass

    def is_alive(self): return self._is_alive

    def serialize(self): return {"name": self.name}