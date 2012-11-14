#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WillhabenObserver.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import time, datetime
from itertools import compress
from Connector import *
from Logger import *
import threading

class Observer(threading.Thread):
    
    def __init__(self, url, profile, store, assessor, notification, logger = Logger(), update_interval = 180, name = u"Unnamed Observer"):
        super(Observer, self).__init__()
        self.interval = update_interval
        self.connector = Connector(url, profile)
        self.store = store
        self.assessor = assessor
        self.notification = notification
        self.logger = logger
        self.daemon = True
        self.name = name
    
    def process_ads(self, ads):
        if len(ads) == 0: return
        hits = map(self.assessor.check, ads)
        hit_ads = [ad for ad in compress(ads, hits)]
        new_ads = self.store.add_ads(hit_ads)
        for ad in new_ads:
            try:
                self.logger.append("Observer Found Ad: " + ad["title"])
            except KeyError:
                self.logger.append("Observer Found Ad: " + ad.key)
            if self.notification:
                self.notification.notifyAll(ad)
        self.time_mark = sorted(ads, key = lambda ad: ad.timetag)[-1].timetag

    def run(self):
        self.time_mark = datetime.datetime.now() - datetime.timedelta(days = 1)
        self.logger.append("Observer {} polling ads back to {}".format(self.name, self.time_mark))
        ads = self.connector.ads_after(self.time_mark)
        self.process_ads(ads)
        self.logger.append("Observer {} initial poll done".format(self.name))
        while True:
            time.sleep(self.interval)
            self.logger.append("Observer {} polling for new ads".format(self.name))
            try:
                ads = self.connector.ads_after(self.time_mark)
                self.process_ads(ads)
            except ConnectionError:
                self.logger.append("No connection to {}".format(self.connector.name))