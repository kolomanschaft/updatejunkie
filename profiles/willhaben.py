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

from bs4 import BeautifulSoup
from . import base
#import base
import re
from datetime import datetime

class WillhabenProfile(base.ProfileBase):
    
    name = "Willhaben"
    base_url = "http://www.willhaben.at"
    
    def __init__(self):
        self._tags = {"id":0, "url":"", "title":"", "price":0.0,
                      "description":"", "image":"", "zip":0, "city":"",
                      "datetime":None}
        
    @property
    def tags(self):
        return self._tags.keys()

    @property
    def key_tag(self):
        return "id"

    @property
    def datetime_tag(self):
        return "datetime"

    @property
    def paging_param(self):
        return "page"

    @property
    def paging_param_init(self):
        return 1

    @property
    def paging_method(self):
        return "GET"

    @property
    def encoding(self):
        return "ISO-8859-1"

    def parse(self, html):
        soup = BeautifulSoup(html)
        allads = soup.find(name="ul", attrs={"id":"resultlist"})
        ads = allads.findAll("li", attrs={"class":"media"})
        return map(self._soup_to_tags, ads)

    def _soup_to_tags(self, soup):
        tags = self._tags.copy()

        # The image URL
        tags["image"] = soup.a.img['src']

        # The ad's URL
        tags["url"] = self.base_url + soup.a['href']

        # The ID (encoded in the ad link)
        id_str = re.findall("adId=([0-9]+)", tags["url"])[0]
        tags["id"] = int(id_str)

        # The title
        tags["title"] = soup.div.a.contents[0].strip()

        # This node contains ZIP code, location and datetime
        seller_details_node = soup.find('p', attrs={'class', 'bot-1'})

        # The datetime
        if (len(seller_details_node.contents) > 4):
            datetime_str = soup.find('p', attrs={'class', 'bot-1'}).contents[4].strip()
        else:
            datetime_str = soup.find('p', attrs={'class', 'bot-1'}).contents[2].strip()
        tags["datetime"] = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")

        # The location
        location_str = seller_details_node.contents[0].strip()
        location_matches = re.match("([0-9]+)[\r\n\s]*(.*$)", location_str, re.M | re.DOTALL).groups(())
        tags["zip"] = location_matches[0]
        tags["city"] = location_matches[1]

        # The price tag (if present)
        price_str = soup.find('p', attrs={'class':'info-2'}).text.strip()
        price_match = re.search("([0-9]+),-", price_str, re.M)
        if price_match:
            tags["price"] = float(price_match.groups()[0])

        # The description
        tags["description"] = soup.find('p', attrs={'class':'info-3'}).text.strip()

        return tags
