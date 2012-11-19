#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
from AdStore import *
from AdAssessor import *
from Observer import *
from Logger import *
from Config import *
from NotificationServer import *
from Profile import *
from threading import Thread
import md5
import sys
import os
import time
import datetime

def pseudo_gui():
    while True:
        time.sleep(1)

if __name__ == "__main__":
    
    # Create the 'files/' directory if it doesn't exist yet
    if not os.path.exists("./files/"): os.mkdir("files")
    
    # Load configuration
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "./files/willhaben.cfg"
    config = Config(config_path)
    
    # Initialize logging
    logger = Logger(path = "files/observer.log")
    
    # Setting up the observers
    # ------------------------
    observers = []
    gui_event_loop = None
    for observer_name in config.list_observers():
        logger.append("Setting up observer " + observer_name)
        observer_config = config.observer_config(observer_name)
        profile = get_profile(observer_config.profile)
        # Ads that have already been processed are registered in this file
        if observer_config.ads_store:
            save_file = u"files/adstore.{}.db".format(observer_name)
        else: 
            save_file = None    
        store = AdStore(path = save_file)
    
        # Search criteria setup
        assessor = AdAssessor()
        for keywords in observer_config.keywords_all:
            criterion = AdCriterionKeywordsAll(keywords["wildcard"], keywords["value"])
            assessor.add_criterion(criterion)
        for keywords in observer_config.keywords_any:
            criterion = AdCriterionKeywordsAny(keywords["wildcard"], keywords["value"])
            assessor.add_criterion(criterion)
        for keywords in observer_config.keywords_not:
            criterion = AdCriterionKeywordsNot(keywords["wildcard"], keywords["value"])
            assessor.add_criterion(criterion)
        for limit in observer_config.limits:
            criterion = AdCriterionLimit(limit["wildcard"], limit["value"])
            assessor.add_criterion(criterion)
    
        # Notification server setup
        notificationServer = NotificationServer()
        if observer_config.gtk_active:
            from platform_dependant.Linux import GTKNotification
            import gtk, gobject
            GTKNotify = GTKNotification(icon = "./logo.png")
            notificationServer.addNotification(GTKNotify)
            gobject.threads_init()
            gui_event_loop = gtk.main
        if observer_config.osx_active:
            import Foundation, objc, AppKit
            from PyObjCTools import AppHelper
            from platform_dependant.MacOS import MountainLionNotification
            formatting = profile.notification_desktop
            MLNotify = MountainLionNotification.alloc().init()
            MLNotify.formatting(formatting[u"title"], formatting[u"body"], formatting[u"url"])
            notificationServer.addNotification(MLNotify)
            app = AppKit.NSApplication.sharedApplication()
            gui_event_loop = AppHelper.runEventLoop
        if observer_config.email_active:
            from platform_dependant.Server import EmailNotification
            formatting = profile.notification_email
            emailNotify = EmailNotification(config.smtp_host,
                                            config.smtp_port,
                                            config.smtp_user,
                                            config.smtp_password,
                                            config.email_from,
                                            observer_config.email_to,
                                            formatting[u"type"],
                                            formatting[u"subject"],
                                            formatting[u"body"])
            notificationServer.addNotification(emailNotify)

        observer = Observer(url = observer_config.url,
                            profile = profile,
                            store = store,
                            assessor = assessor,
                            notification = notificationServer,
                            logger = logger,
                            update_interval = observer_config.update_interval,
                            name = observer_name)
        observers.append(observer)
    
    # all done! let's start spinning the wheel
    for observer in observers: observer.start()
    if gui_event_loop:
        gui_event_loop()
    else:
        pseudo_gui()
