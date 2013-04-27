#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WillhabenConnector.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlencode
import re
from AdStore import Ad
from Profile import *
import datetime
import html.parser
from threading import Lock

class ConnectionError(Exception): pass

class Connector():
    
    @property
    def profile_name(self):
        return self._profile.name
    
    def __init__(self, url, profile):
        m = re.match(r"(http://)?([a-zA-Z0-9-.]+)?([a-zA-Z0-9-._/?=&%]*)", url)
        if m is None:
            raise Exception("Invalid URL: {}".format(url))
        self._url = url
        if isinstance(profile, Profile):
            self._profile = profile
        elif isinstance(profile, str) or isinstance(profile, str):
            self._profile = get_profile(profile)

    def __get_page__(self, page):
        data = None
        if page is not None:
            page_param = self._profile.page_param
            new_encoded = urlencode({page_param["name"]: page})
            if page_param["method"] == "GET":
                page_match = re.search("{}=[0-9]+".format(page_param["name"]), self._url)
                if page_match:
                    self._url = self._url.replace(page_match.group(), new_encoded)
                elif self._url.find("?") >= 0:
                    self._url = self._url + "&" + new_encoded
                else:
                    self._url = self._url + "?" + new_encoded
            else:
                data = new_encoded
        
        try:
            f = urllib.request.urlopen(self._url, data)
        except urllib.error.URLError:
            raise ConnectionError("Could not connect to {}".format(self._url))
        
        html = str(f.read(), "ISO-8859-1")
        f.close()
        for regex in self._profile.format_regexes:
            if regex["type"] == "filter":
                html = re.sub(regex["regex"], "", html)
            else:
                raise ConnectionError("Format type {} is not implemented!".format(regex["type"]))
        return html


    def __get_adlist_from_html__(self, html):
        def text_tag(value):
            return html.parser.HTMLParser().unescape(value)
        def integer_tag(value):
            try:
                return int(value)
            except ValueError:
                return float("nan")
        def float_tag(value):
            try:
                return float(value.replace(",", "."))
            except ValueError:
                return float("nan")
        def url_tag(value):
            if value[0] == "/":
                return self._profile.base_url + value[1:]
            else:
                return value

        ad_tuples = re.findall(self._profile.ad_regex, html)
        tags = self._profile.ad_tags
        
        ads = []
        for ad_tuple in ad_tuples:
            ad = Ad()
            for combined in zip(tags, ad_tuple):
                if combined[0]["type"] == "text":
                    ad[combined[0]["name"]] = text_tag(combined[1])
                elif combined[0]["type"] == "integer":
                    ad[combined[0]["name"]] = integer_tag(combined[1])
                elif combined[0]["type"] == "float":
                    ad[combined[0]["name"]] = float_tag(combined[1])
                elif combined[0]["type"] == "url":
                    ad[combined[0]["name"]] = url_tag(combined[1])
            ad.keytag = self._profile.key_tag
            timetag_info = self._profile.time_tag
            ad.timetag = datetime.datetime.strptime(ad[timetag_info["name"]], timetag_info["format"])
            ad["listingUrl"] = self._url
            ads.append(ad)
        return ads
            
    
    def frontpage_ads(self):
        if not self._profile.page_param:
            html = self.__get_page__(None)
        else:
            html = self.__get_page__(self._profile.page_param["init"])
        return self.__get_adlist_from_html__(html)
    
    def ads_all(self, pagestart = None, maxpages = 100):
        timelimit = datetime.datetime(1970,1,1)
        return self.ads_after(timelimit, maxpages)
    
    def ads_in(self, dtime, maxpages = 100):
        if not isinstance(dtime, datetime.timedelta):
            raise ConnectionError("timelimit needs to be a timedelta instance")
        timelimit = datetime.datetime.now() - dtime
        return self.ads_after(timelimit, maxpages)
    
    def ads_after(self, timelimit, maxpages = 100):
        if not self._profile.page_param:
            ads = self.frontpage_ads()
            return [ad for ad in ads if ad.timetag > timelimit]
        pagestart = self._profile.page_param["init"]
        if not isinstance(timelimit, datetime.datetime):
            raise ConnectionError("timelimit needs to be a datetime instance")
        ads = []
        for page in range(pagestart,pagestart+maxpages):
            html = self.__get_page__(page)
            new_ads = [ad for ad in self.__get_adlist_from_html__(html) if ad.timetag > timelimit]
            if len(new_ads) == 0:
                break
            ads.extend(new_ads)
        return ads

if __name__ == "__main__":
    url = "http://www.willhaben.at/iad/kaufen-und-verkaufen/moebel-wohnen-buero/regale-schraenke-vitrinen-kommoden/"
    c = Connector(url, "willhaben")
    #html = c.__get_page__(1)
    #print c.__get_adlist_from_html__(html)
    #print [ad.key for ad in c.__get_adlist_from_html__(html)]
    print([ad.timetag for ad in c.ads_in(datetime.timedelta(hours = 2))])
    