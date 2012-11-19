#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MacOS.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
from Notification import *
import Foundation
import objc
import AppKit
from PyObjCTools import AppHelper
from threading import Thread

class MountainLionNotification(Foundation.NSObject, Notification):
    
    def formatting(self, title, body, url):
        self.title = unicode(title)
        self.body = unicode(body)
        self.url = url

    def notify(self, ad):
        NSUserNotification = objc.lookUpClass('NSUserNotification')
        NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(self.title.format(**ad))
        try:
            notification.setSubtitle_(u"for € " + unicode(str(ad["price"])))
        except KeyError: pass
        notification.setInformativeText_(self.body.format(**ad))
        notification.setSoundName_("NSUserNotificationDefaultSoundName")
        notification.setHasActionButton_(True)
        notification.setOtherButtonTitle_("View")
        try:
            notification.setUserInfo_({"action":"open_url", "value":self.url.format(**ad)})
        except KeyError: pass
        NSUserNotificationCenter.defaultUserNotificationCenter().setDelegate_(self)
        NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)

    def userNotificationCenter_didActivateNotification_(self, center, notification):
        userInfo = notification.userInfo()
        if userInfo["action"] == "open_url":
            import subprocess
            subprocess.Popen(['open', userInfo["value"]])