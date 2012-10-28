#!/usr/bin/env python
# encoding: utf-8
"""
NotificationServer.py

Created by Martin Hammerschmied on 2012-10-28.
Copyright (c) 2012. All rights reserved.
"""
from platform_dependant.Notification import *

class NotificationServer:
    
    def __init__(self):
        self.notifications = []
    
    def addNotification(self, notification):
        if not isinstance(notification, Notification):
            raise TypeError("Passed objects is not a 'Notification' type")
        self.notifications.append(notification)

    
    def addNotifications(self, *args):
        for notification in args:
            self.addNotification(notification)

    def notifyAll(self, *args, **kwargs):
        for notification in self.notifications:
            notification.notify(*args, **kwargs)
    
    def __getitem__(self, key):
        return self.notifications[key]
    
    def __delitem__(self, key):
        del self.notifications[key]
