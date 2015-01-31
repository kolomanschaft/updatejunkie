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

import sys
from profile import *
from connector import *
from adstore import *
import pprint

if __name__ == "__main__":
    try:
        profile = str(sys.argv[1])
        url = str(sys.argv[2])
    except IndexError:
        print("Arguments error!")
        print("Usage: python profile_tester.py profile_name url")
        exit()
    pp = pprint.PrettyPrinter()
    print("\n\nTesting Profile '{}'".format(profile))
    print("with URL", url)
    
    def print_ads(ads):
        for ad in ads:
            try:
                keytag = ad['id']
                print("\nAd-ID:", keytag)
            except AdKeyError:
                print("\nNo keytag set! Set ad.keytag")
            print("Tags:")
            pp.pprint(ad)
            try:
                timetag = ad['datetime']
                print("TimeTag:", timetag)
            except AdKeyError:
                print("No timetag!")

    c = Connector(url, profile)
    ads = c.frontpage_ads()
    print_ads(ads)
