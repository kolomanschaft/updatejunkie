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

import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlencode
import re
from adstore import Ad
import datetime
import html.parser as htmlparser
from threading import Lock
import profiles

class ConnectionError(Exception): pass

class Connector():
    
    @property
    def profile_name(self):
        return self._profile.name
    
    @property
    def url(self):
        return self._url
    
    def __init__(self, url, profile):
        m = re.match(r"(http://)?([a-zA-Z0-9-.]+)?([a-zA-Z0-9-._/?=&%]*)", url)
        if m is None:
            raise Exception("Invalid URL: {}".format(url))
        self._url = url
        if isinstance(profile, profiles.base.ProfileBase):
            self._profile = profile
        elif isinstance(profile, str):
            self._profile = profiles.get_profile_by_name(profile)

    def _get_page(self, page):
        data = None
        url = self._url
        if page is not None:
            page_param = self._profile.paging_param
            new_encoded = urlencode({page_param: page})
            if self._profile.paging_method == "GET":
                page_match = re.search("{}=[0-9]+".format(page_param), self._url)
                if page_match:
                    url = self._url.replace(page_match.group(), new_encoded)
                elif self._url.find("?") >= 0:
                    url = self._url + "&" + new_encoded
                else:
                    url = self._url + "?" + new_encoded
            else:
                data = new_encoded
        
        try:
            f = urllib.request.urlopen(url, data)
        except urllib.error.URLError:
            raise ConnectionError("Could not connect to {}".format(url))
        
        html = str(f.read(), self._profile.encoding)
        f.close()
        return html

    def frontpage_ads(self):
        if not self._profile.paging_param:
            html = self._get_page(None)
        else:
            html = self._get_page(self._profile.paging_param_init)
        return self._profile.parse(html)
    
    def ads_all(self, pagestart = None, maxpages = 10):
        timelimit = datetime.datetime(1970,1,1)
        return self.ads_after(timelimit, maxpages)
    
    def ads_in(self, dtime, maxpages = 10):
        if not isinstance(dtime, datetime.timedelta):
            raise ConnectionError("timelimit needs to be a timedelta instance")
        timelimit = datetime.datetime.now() - dtime
        return self.ads_after(timelimit, maxpages)
    
    def ads_after(self, timelimit, maxpages = 10):
        if not self._profile.paging_param:
            ads = self.frontpage_ads()
            return [ad for ad in ads if ad.timetag > timelimit]

        pagestart = int(self._profile.paging_param_init)

        if not isinstance(timelimit, datetime.datetime):
            raise ConnectionError("timelimit needs to be a datetime instance")

        ads = []
        for page in range(pagestart,pagestart+maxpages):
            html = self._get_page(page)
            new_ads = [Ad(tags, self._profile.key_tag, self._profile.datetime_tag)
                       for tags in self._profile.parse(html)
                       if tags[self._profile.datetime_tag] > timelimit]

            if len(new_ads) == 0:
                break
            ads.extend(new_ads)

        return ads
