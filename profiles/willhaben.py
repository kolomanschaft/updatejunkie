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
import re

class WillhabenProfile(base.ProfileBase):
    
    name = "Willhaben"
    base_url = "http://www.willhaben.at"
    
    def __init__(self):
        self._tags = {"id":0, "url":"", "title":"", "price":0.0, "description":""}
        
    @property
    def tags(self):
        return self._tags.keys()

    def parse(self, html):
        soup = BeautifulSoup(html)
        allads = soup.find(name="ul", attrs={"id":"resultlist"})
        ads = allads.findAll("li", attrs={"class":"even clearfix"})
        ads.extend(allads.findAll("li", attrs={"class":"odd clearfix"}))
        return list(map(self._ad_soup_to_dict, ads))

    def _ad_soup_to_dict(self, soup):
        tags = self._tags.copy()
        tags["id"] = int(soup.h2.attrs['id'])
        tags["url"] = self.base_url + soup.h2.a.attrs['href']        

        tags["title"] = soup.h2.a.text.strip()
        
        price_text = soup.find('p', attrs={'class':'price'}).text
        price_match = re.search("^.*?([0-9]+),([0-9]{2})", price_text, re.M)
        if price_match:
            tags["price"] = float(price_match.groups()[0]) + float(price_match.groups()[1])/100
        
        description_text = soup.find('p', attrs={'class':'description'}).text
        lines = re.findall("^[\r\n\s]*([^\r^\n]+)[\r\n\s]*", description_text)
        if len(lines) > 0:
            tags["description"] = lines[0]

        return tags
    

if __name__ == "__main__":

    from urllib import request
    from pprint import PrettyPrinter

    with request.urlopen("http://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?KITCHENAPPLIANCES_DETAIL=4&CATEGORY/SUBCATEGORY=8599&CATEGORY/MAINCATEGORY=8214") as f:
        html = f.read()
    
    p = WillhabenProfile()
    ads = p.parse(html)
    
    pp = PrettyPrinter()
    pp.pprint(ads)
    