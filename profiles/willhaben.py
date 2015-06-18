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

import re
import urllib.parse
import itertools

from bs4 import BeautifulSoup
from . import base
from datetime import datetime
from enum import Enum

class Rubric(Enum):
    USED_CARS = 1
    MARKET_PLACE = 2

class WillhabenProfile(base.ProfileBase):
    
    name = "Willhaben"
    base_url = "http://www.willhaben.at"
    
    def __init__(self):
        self._tags = {"id":0,   # unique ID
                      "url":"", # Details page
                      "title":"",   # Ad title
                      "price":0.0,  # price (if present)
                      "description":"", # Snippet of description from listing (Only MARKET_PLACE)
                      "image":"",   # Image URL
                      "zip":0,  # ZIP code of seller
                      "city":"",    # City of seller
                      "datetime":None,  # In case of used cars this is the time of polling
                      "milage": 0,  # USED_CARS only
                      "year": 0,    # Year of construction (USED_CARS only)
                      "horsepower": 0,    # USED_CARS only
                      "fuel": 0}    # Type of fuel (USED_CARS only)

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
    def encoding(self):
        return "ISO-8859-1"

    def first_page(self, url):
        url_components = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_components[4]))
        query["page"] = 1
        url_components[4] = urllib.parse.urlencode(query)
        return urllib.parse.urlunparse(url_components)

    def next_page(self, url):
        url_components = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_components[4]))
        if "p" in query:
            query["page"] = int(query["page"]) + 1
        else:
            query["p"] = 1
        url_components[4] = urllib.parse.urlencode(query)
        return urllib.parse.urlunparse(url_components)

    def parse(self, html):
        soup = BeautifulSoup(html)
        description_header = soup.head.find('meta', attrs={'name': 'description'}).attrs['content']
        if description_header.find('Gebrauchtwagen') >= 0:
            rubric = Rubric.USED_CARS
        elif description_header.find('Marktplatz') >= 0:
            rubric = Rubric.MARKET_PLACE
        else:
            raise HTMLParseError("Could not determine the willhaben.at rubric")
        allads = soup.find(name="ul", attrs={"id":"resultlist"})
        if not allads:
            return []
        ads = allads.findAll("li", attrs={"class":"media"})
        return map(self._soup_to_tags, ads, itertools.repeat(rubric, len(ads)))

    def _soup_to_tags(self, soup, rubric):
        tags = self._tags.copy()

        # The image URL
        tags["image"] = soup.a.img['src']

        # The ad's URL
        tags["url"] = self.base_url + soup.a['href']

        # The ID
        id_str = soup.div.a.attrs['id']
        tags["id"] = int(id_str)

        # The title
        tags["title"] = soup.div.find_all('a')[1].span.contents[0].strip()

        # This node contains ZIP code, location and datetime
        seller_details_node = soup.find('p', attrs={'class', 'bot-1'})

        # The datetime
        if rubric == Rubric.MARKET_PLACE:
            datetime_str = soup.find('p', attrs={'class', 'bot-1'}).span.contents[-1].strip()
            tags["datetime"] = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
        elif rubric == Rubric.USED_CARS:
            tags["datetime"] = datetime.now()   # used cars ads have no datetime

        # The location
        location_str = seller_details_node.span.contents[0].strip()
        (zip, city) = re.match("([0-9]+)?\W*(.*)", location_str, re.M | re.DOTALL).groups(())
        if zip: tags["zip"] = zip
        if city: tags["city"] = city

        subtitle_str = soup.find('p', attrs={'class':'info-2'}).text.strip()
        if rubric == Rubric.MARKET_PLACE:
            subtitle_match = re.search(r"([0-9]+),-", subtitle_str, re.M)
            if subtitle_match:
                tags["price"] = float(subtitle_match.groups()[0])
        elif rubric == Rubric.USED_CARS:
            subtitle_match = re.match(r"([0-9]{4})\W*([0-9.]+)\W*km\W*([0-9.]+)?", subtitle_str, re.M)
            if subtitle_match:
                (year, milage, price) = subtitle_match.groups()
                tags["year"] = int(year)
                tags["milage"] = int(milage.replace(".", ""))
                if price is not None: tags["price"] = float(price.replace(".", ""))

        # The description
        if rubric == Rubric.MARKET_PLACE:
            tags["description"] = soup.find('p', attrs={'class':'info-3'}).text.strip()
        elif rubric == Rubric.USED_CARS:
            details_str = soup.find('p', attrs={'class':'info-3'}).text.strip()
            subtitle_match = re.match(r"([0-9.]+)\W*kW\W*\(([0-9.]+)\W*PS\)\W*([a-zA-Z ]+)\W*(.*)", details_str, re.M)
            if subtitle_match:
                (_, horsepower, fuel, _) = subtitle_match.groups()
                tags["horsepower"] = float(horsepower)
                tags["fuel"] = fuel

        return tags
