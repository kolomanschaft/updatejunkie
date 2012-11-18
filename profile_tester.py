#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
profile_tester.py

Created by Martin Hammerschmied on 2012-11-12.
Copyright (c) 2012. All rights reserved.
"""
import sys
from Profile import *
from Connector import *
from AdStore import *
import pprint

if __name__ == "__main__":
    try:
        profile = unicode(sys.argv[1])
        url = unicode(sys.argv[2])
    except IndexError:
        print "Arguments error!"
        print "Usage: python profile_tester.py profile_name url"
        exit()
    pp = pprint.PrettyPrinter()
    print "\n\nTesting Profile '{}'".format(profile)
    print "with URL", url
    
    def print_ads(ads):
        for ad in ads:
            try:
                keytag = ad.key
                print "\nAd-ID:", keytag
            except AdKeyError:
                print "\nNo keytag set! Set ad.keytag"
            print "Tags:"
            pp.pprint(ad)
            try:
                timetag = ad.timetag
                print "TimeTag:", timetag
            except AdKeyError:
                print "No timetag!"

    c = Connector(url, profile)
    print "Ad REGEX:", c._profile.ad_regex
    ads = c.frontpage_ads()
    print_ads(ads)

    print "\n{} ads found on the first page".format(len(ads))
