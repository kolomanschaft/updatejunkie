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

import unittest
import os
import random
from adstore import *


class TestAdStore(unittest.TestCase):
    
    path = "./testStore.save"
    
    def setUp(self):
        self.store = AdStore(self.path)
        self.some_ads = [Ad({"id":nr, "dt": nr, "title":"Ad number {}".format(nr)}, "id", "dt")
                         for nr in range(10)]

    def tearDown(self):
        os.remove(self.path)
        
    def test_add_and_remove_ads(self):
        added_ads = self.store.add_ads(self.some_ads)
        self.assertListEqual(self.some_ads, added_ads)
        ridx = [2,3,5,6,8]
        ads_to_remove = [self.some_ads[i] for i in ridx]
        removed = self.store.remove_ads(ads_to_remove)
        self.assertListEqual(ads_to_remove, removed)
        ads_not_removed = [ad for ad in self.some_ads if ad.key not in ridx]
        self.assertListEqual(ads_not_removed, self.store[:])
    
    def test_save_and_load_ads(self):
        self.store.add_ads(self.some_ads)
        self.store.save()
        another_store = AdStore(self.path)
        first_ids = [ad.key for ad in self.some_ads]
        second_ids = [ad.key for ad in another_store]
        self.assertListEqual(first_ids, second_ids)

    def test_sort_by_date(self):
        delta = datetime.timedelta(hours = 2)
        for ad in self.some_ads:
            ad.datetime = datetime.datetime.now() + random.randint(0,20) * delta
        self.store.add_ads(self.some_ads)
        for i in range(1,self.store.length()):
            self.assertGreaterEqual(self.store[i].datetime, self.store[i-1].datetime)
