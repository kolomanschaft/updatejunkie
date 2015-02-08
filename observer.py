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

import time
import datetime
import threading
import logging

from itertools import compress
from connector import Connector, ConnectionError


class Observer(threading.Thread):

    # observer states
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    
    def __init__(self, url, profile, store, assessor, notifications, update_interval = 180, name = "Unnamed Observer"):
        super(Observer, self).__init__()
        self._interval = update_interval
        self._connector = Connector(url, profile)
        self._store = store
        self._assessor = assessor
        self._notifications = notifications
        self._name = name
        self._quit = False
        self._time_mark = datetime.datetime.now() - datetime.timedelta(days = 1)
        self._state = Observer.RUNNING
        self.name = name
    
    def serialize(self):
        d = dict()
        d["name"] = self._name
        d["state"] = self._state
        d["url"] = self._connector.url
        d["interval"] = self._interval
        d["profile"] = self._connector.profile_name
        if self._store is not None:
            d["store"] = True
        if self._assessor is not None:
            d["criteria"] = [criterion.serialize() for criterion in self._assessor.criteria]
        # if self._notifications is not None:
        #     d["notifications"] = [notification.serialize() for notification in self._notifications]
        return d

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def quit(self):
        """
        Make the Thread quit
        """
        self._quit = True

    def _process_ads(self, ads):
        if len(ads) == 0: return
        hits = map(self._assessor.check, ads)
        hit_ads = [ad for ad in compress(ads, hits)]
        new_ads = self._store.add_ads(hit_ads)
        for ad in new_ads:
            try:
                logging.info("Observer '{}' Found Ad: {}".format(self._name, ad["title"]))
            except KeyError:
                logging.info("Observer '{}' Found Ad: {}".format(self._name, ad.key))
            if self._notifications:
                self._notifications.notify_all(ad)
        self._time_mark = sorted(ads, key = lambda ad: ad.datetime)[-1].datetime

    def run(self):
        self._state = Observer.RUNNING
        while True:
            if self._state == Observer.RUNNING:
                logging.info("Observer '{}' polling for new ads since {}".format(self._name, self._time_mark))
                try:
                    ads = self._connector.ads_after(self._time_mark)
                    if self._quit:
                        return   # Quit now if quit() was called while fetching ads

                    self._process_ads(ads)

                except ConnectionError as ex:
                    logging.info("Observer '{}' connection failed with message: {}".format(self._name, ex.args[0]))

            # going to sleep
            next_time = datetime.datetime.now() + datetime.timedelta(seconds=self._interval)
            while datetime.datetime.now() < next_time:
                time.sleep(1)
                if self._quit:
                    return   # Quit now if quit() was called while sleeping
