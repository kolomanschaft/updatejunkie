#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdStore.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import pickle
import datetime
from threading import RLock

class AdKeyError(Exception):pass

class Ad(dict):

    @property
    def keytag(self):
        return self._keytag
    
    @keytag.setter
    def keytag(self, tagname):
        if not tagname in self.keys():
            raise AdKeyError("Tag {0} could not be found. Set the tag {0} before using it as key!".format(tagname))
        self._keytag = tagname
    
    @property
    def key(self):
        if not hasattr(self, "_keytag"):
            raise AdKeyError("No keytag defined yet!")
        return self[self._keytag]
    
    @property
    def timetag(self):
        if not hasattr(self, "_timetag"):
            raise AdKeyError("No timetag set yet!")
        return self._timetag
    
    @timetag.setter
    def timetag(self, atime):
        if not isinstance(atime, datetime.datetime):
            raise TypeError("The timetag needs to be a valid datetime!")
        self._timetag = atime

class AdStore(object):
    
    def __init__(self, path = None, autosave = True, autosort = True):
        """
        'flag' has the same meaning as the 'flag' parameter in anydbm.open()
        """
        self.path = path
        self.autosave = autosave
        self.autosort = autosort
        self._lock = RLock()
        self.load()
    
    def _sort_by_date(self):
        try:
            self.ads = sorted(self.ads, key = lambda ad: ad.timetag)
        except AdKeyError:
            pass
    
    def length(self):
        return len(self.ads)
    
    def save(self):
        self._lock.acquire()
        if not self.path: return
        try:
            with open(self.path, "wb") as f:
                pickler = pickle.Pickler(f)
                pickler.dump(self.ads)
        except: raise
        self._lock.release()
        return True
    
    def load(self):
        self._lock.acquire()
        if not self.path:
            self.ads = []
            self._lock.release()
            return
        try:
            with open(self.path, "rb") as f:
                unpickler = pickle.Unpickler(f)
                self.ads = unpickler.load()
        except EOFError: pass
        except IOError: pass
        finally:
            if not hasattr(self, "ads"): self.ads = []
            self._lock.release()

    
    def add_ads(self, ads):
        """
        'ads' is a list of new ads
        """
        self._lock.acquire()
        added_ads = []
        cur_keys = [ad.key for ad in self.ads]
        new_keys = [ad.key for ad in ads]
        for i in range(len(new_keys)):
            if new_keys[i] not in cur_keys:
                self.ads.append(ads[i])
                added_ads.append(ads[i])
        if self.autosort: self._sort_by_date()
        if self.autosave: self.save()
        self._lock.release()
        return added_ads
    
    def remove_ads(self, ads):
        self._lock.acquire()
        removed_ads = []
        cur_keys = [ad.key for ad in self.ads]
        new_keys = [ad.key for ad in ads]
        for i in range(len(new_keys)):
            if new_keys[i] in cur_keys:
                idx = cur_keys.index(new_keys[i])
                del self.ads[idx]
                del cur_keys[idx]
                removed_ads.append(ads[i])
        if self.autosort: self._sort_by_date()
        if self.autosave: self.save()
        self._lock.release()
        return removed_ads
    
    def __getitem__(self, key):
        return self.ads[key]