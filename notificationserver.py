#!/usr/bin/env python3
# encoding: utf-8
"""
NotificationServer.py

Created by Martin Hammerschmied on 2012-10-28.
Copyright (c) 2012. All rights reserved.
"""
from platform_dependant.Notification import *

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
