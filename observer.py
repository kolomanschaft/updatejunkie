#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WillhabenObserver.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import time, datetime
from itertools import compress
from Connector import Connector, ConnectionError
from Logger import Logger
import threading

class Observer(threading.Thread):
    
    def __init__(self, url, profile, store, assessor, notifications, logger = Logger(), update_interval = 180, name = "Unnamed Observer"):
        super(Observer, self).__init__()
        self.interval = update_interval
        self.connector = Connector(url, profile)
        self.store = store
        self.assessor = assessor
        self.notifications = notifications
        self.logger = logger
        self.name = name
        self._quit = False
    
    def serialize(self):
        d = dict()
        d["name"] = self.name
        d["url"] = self.connector.url
        d["interval"] = self.interval
        d["profile"] = self.connector.profile_name
        if self.store is not None:
            d["store"] = True
        if self.assessor is not None:
            d["criteria"] = [criterion.serialize() for criterion in self.assessor.criteria]
        if self.notifications is not None:
            d["notifications"] = [notification.serialize() for notification in self.notifications]
        return d
        
    def quit(self):
        """
        Make the Thread quit on the next round.
        """
        self._quit = True
        self.logger.append("Observer {} quits on the next round".format(self.name))

    def process_ads(self, ads):
        if len(ads) == 0: return
        hits = map(self.assessor.check, ads)
        hit_ads = [ad for ad in compress(ads, hits)]
        new_ads = self.store.add_ads(hit_ads)
        for ad in new_ads:
            try:
                self.logger.append("Observer {} Found Ad: {}".format(self.name, ad["title"]))
            except KeyError:
                self.logger.append("Observer {} Found Ad: {}".format(self.name, ad.key))
            if self.notifications:
                self.notifications.notify_all(ad)
        self.time_mark = sorted(ads, key = lambda ad: ad.timetag)[-1].timetag

    def run(self):
        self.time_mark = datetime.datetime.now() - datetime.timedelta(days = 1)
        self.logger.append("Observer {} polling ads back to {}".format(self.name, self.time_mark))
        ads = self.connector.ads_after(self.time_mark)
        if self._quit: return   # Quit now if quit() was called while fetching ads
        self.process_ads(ads)
        self.logger.append("Observer {} initial poll done".format(self.name))
        while True:
            time.sleep(self.interval)
            if self._quit: return   # Quit now if quit() was called while sleeping
            self.logger.append("Observer {} polling for new ads".format(self.name))
            try:
                ads = self.connector.ads_after(self.time_mark)
                if self._quit: return   # Quit now if quit() was called while fetching ads
                self.process_ads(ads)
            except ConnectionError as ex:
                self.logger.append("Observer {} connection failed with message: {}".format(self.name, ex.message))
