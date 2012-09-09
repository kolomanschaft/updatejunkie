#!/usr/bin/env python
# encoding: utf-8
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

	def notify(self, title, subtitle, text, url):
		NSUserNotification = objc.lookUpClass('NSUserNotification')
		NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')
		notification = NSUserNotification.alloc().init()
		notification.setTitle_(str(title))
		notification.setSubtitle_(str(subtitle))
		notification.setInformativeText_(str(text))
		notification.setSoundName_("NSUserNotificationDefaultSoundName")
		notification.setHasActionButton_(True)
		notification.setOtherButtonTitle_("View")
		notification.setUserInfo_({"action":"open_url", "value":url})
		NSUserNotificationCenter.defaultUserNotificationCenter().setDelegate_(self)
		NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)

	def userNotificationCenter_didActivateNotification_(self, center, notification):
		userInfo = notification.userInfo()
		if userInfo["action"] == "open_url":
			import subprocess
			subprocess.Popen(['open', userInfo["value"]])