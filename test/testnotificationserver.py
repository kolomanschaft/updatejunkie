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
from notificationserver import *
from notifications import *


class TestNotificationServer(unittest.TestCase):
    
    def setUp(self):
        self.notificationServer = NotificationServer()
    
    def tearDown(self):
        del self.notificationServer
    
    def test_notification_type_error(self):
        x = 123
        self.assertRaises(TypeError, self.notificationServer.add_notification, x)
    
    def test_add_delete_notificaions(self):
        a = Notification()
        b = Notification()
        self.notificationServer.add_notifications(a,b)
        self.assertIs(self.notificationServer[0], a)
        self.assertIs(self.notificationServer[1], b)
        self.assertRaises(IndexError, self.notificationServer.__getitem__, 2)
        del self.notificationServer[0]
        self.assertIs(self.notificationServer[0], b)        
        self.assertRaises(IndexError, self.notificationServer.__getitem__, 1)