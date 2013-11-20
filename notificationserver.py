#!/usr/bin/env python3
# encoding: utf-8
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

from notifications import Notification

class NotificationServer:
    
    def __init__(self):
        self._notifications = []
    
    def add_notification(self, notification):
        if not isinstance(notification, Notification):
            raise TypeError("Passed objects is not a 'Notification' type")
        self._notifications.append(notification)

    
    def add_notifications(self, *args):
        for notification in args:
            self.add_notification(notification)

    def notify_all(self, *args, **kwargs):
        for notification in self._notifications:
            notification.notify(*args, **kwargs)
    
    def __getitem__(self, key):
        return self._notifications[key]
    
    def __iter__(self):
        return self._notifications.__iter__()
    
    def __delitem__(self, key):
        del self._notifications[key]
