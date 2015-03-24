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
import urllib.request
from profiles import willhaben

class TestWillhabenProfile(unittest.TestCase):

    def setUp(self):
        self._profile = willhaben.WillhabenProfile()

    def _get_page(self, url):
        f = urllib.request.urlopen(url)
        html = f.read()
        return html

    def test_used_cars_rubric(self):
        url = "http://www.willhaben.at/iad/gebrauchtwagen/auto/van"
        html = self._get_page(url)
        ads = list(self._profile.parse(html))
        self.assertTrue(len(ads) > 0)
        tags_to_check = [("id", all),
                         ("url", all),
                         ("title", all),
                         ("price", any),
                         ("image", all),
                         ("zip", any),
                         ("city", any),
                         ("datetime", all),
                         ("milage", all),
                         ("year", all),
                         ("horsepower", all),
                         ("fuel", all),]
        for (tag, func) in tags_to_check:
            value_set_in_ad = [ad[tag] != self._profile._tags[tag] for ad in ads]
            self.assertTrue(func(value_set_in_ad), "Tag '{}' seems to be broken".format(tag))

    def test_market_place_rubric(self):
        url = "http://www.willhaben.at/iad/kaufen-und-verkaufen/buecher-filme-musik/cd-dvd-zubehoer/"
        html = self._get_page(url)
        ads = list(self._profile.parse(html))
        self.assertTrue(len(ads) > 0)
        tags_to_check = [("id", all),
                         ("url", all),
                         ("title", all),
                         ("description", all),
                         ("price", any),
                         ("image", all),
                         ("zip", any),
                         ("city", any),
                         ("datetime", all)]
        for (tag, func) in tags_to_check:
            value_set_in_ad = [ad[tag] != self._profile._tags[tag] for ad in ads]
            self.assertTrue(func(value_set_in_ad), "Tag '{}' seems to be broken".format(tag))