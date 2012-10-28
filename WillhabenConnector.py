#!/usr/bin/env python
# encoding: utf-8
"""
WillhabenConnector.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import httplib
from bs4 import BeautifulSoup as bs
import re
from AdStore import Ad

class WillhabenConnectionError(Exception): pass

class WillhabenConnector():
    
    def __init__(self, url):
        m = re.match("(http:\/\/)?([a-zA-Z0-9-.]+)?([a-zA-Z0-9-._/?=&%]*)", url)
        if m is None:
            raise Exception("Invalid URL: {}".format(url))
        self.host = "www.willhaben.at"
        self.url = m.groups()[2]

    def __get_page__(self, page):
        page_match = re.search("page=[0-9]+", self.url)
        if page_match:
            self.url = self.url.replace(page_match.group(), "page="+str(page))
        elif self.url.find("?") >= 0:
            self.url = self.url + "&page="+str(page)
        else:
            self.url = self.url + "?page="+str(page)
        willhaben = httplib.HTTPConnection(self.host)
        try:
            willhaben.request("GET", self.url)
            response = willhaben.getresponse()
        except:
            raise WillhabenConnectionError()
        html = unicode(response.read(), errors = "ignore")
        return html

    def __get_adlist_from_html__(self, html):
        doc = bs(html)
        ads = []
        for li in doc.find_all("li"):
            try:
                if "clearfix" in li["class"]:
                    new_ad = Ad(aid = int(li.h2["id"]),
                                title = unicode(li.h2.a.contents[0]),
                                url = unicode("http://" + self.host + li.h2.a["href"]))
                    for content in li.p.contents:
                        m = re.search("[,0-9]+", content.string)
                        if m:
                            new_ad["price"] = float(m.group().replace(",", "."))
                    ads.append(new_ad)
            except KeyError:
                continue
        return ads
    
    def frontpage_ads(self):
        html = self.__get_page__(1)
        ads = self.__get_adlist_from_html__(html)
        return ads
    
    def all_ads(self, pagestart = 1, maxpages = 100):
        all_ads = []
        for page in range(pagestart,pagestart+maxpages):
            html = self.__get_page__(page)
            ads = self.__get_adlist_from_html__(html)
            if len(ads) == 0:
                break
            all_ads.extend(ads)
        return all_ads