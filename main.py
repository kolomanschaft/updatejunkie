#!/usr/bin/env python3
# encoding: utf-8
"""
main.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
from AdStore import AdStore
from AdAssessor import *
from Observer import Observer
from Logger import Logger
from Config import Config
from NotificationServer import NotificationServer
from Profile import get_profile
from threading import Lock

import sys
import os
import time
import datetime

def server_loop():
    # this is where we should listen on a socket for new configurations
    while True:
        time.sleep(1)

def setup_lock(name):
    lock = Lock()
    globals()[name] = lock

if __name__ == "__main__":
 
    dtime = "01.05.2013 23:27"
    format = "%d.%m.%Y %H:%M"
    datetime.datetime.strptime(dtime, format)
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
    
    # Initialize some locks
    setup_lock("strptime")
    
    # Setting up the observers
    # ------------------------
    observers = []
    for observer_name in config.list_observers():
        logger.append("Setting up observer " + observer_name)
        observer_config = config.observer_config(observer_name)
        #profile = get_profile(observer_config.profile)
        profile = get_profile(observer_config.profile)
        # Ads that have already been processed are registered in this file
        if observer_config.ads_store:
            save_file = "files/adstore.{}.db".format(observer_name)
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
        if observer_config.email_active:
            from platform_dependant.Notification import EmailNotification
            formatting = profile.Notifications.Email
            emailNotify = EmailNotification(config.smtp_host,
                                            config.smtp_port,
                                            config.smtp_user,
                                            config.smtp_password,
                                            formatting.From,
                                            observer_config.email_to,
                                            formatting.ContentType,
                                            formatting.Subject,
                                            formatting.Body.valueOf_)
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
    server_loop()
