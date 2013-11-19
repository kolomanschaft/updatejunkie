#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unittests.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import unittest
import os
import datetime
import random
from adstore import *
from adassessor import *
from logger import *
from notificationserver import *
from platform_dependant.Notification import *
from connector import *

class TestAdStore(unittest.TestCase):
    
    path = "./testStore.save"
    
    def setUp(self):
        self.store = AdStore(self.path)
        self.some_ads = [Ad({"id":nr, "title":"Ad number {}".format(nr)}) for nr in range(10)]
        for ad in self.some_ads:
            ad.keytag = "id"
        
    def tearDown(self):
        os.remove(self.path)
        
    def testAddAndRemoveAds(self):
        added_ads = self.store.add_ads(self.some_ads)
        self.assertListEqual(self.some_ads, added_ads)
        ridx = [2,3,5,6,8]
        ads_to_remove = [self.some_ads[i] for i in ridx]
        removed = self.store.remove_ads(ads_to_remove)
        self.assertListEqual(ads_to_remove, removed)
        ads_not_removed = [ad for ad in self.some_ads if ad.key not in ridx]
        self.assertListEqual(ads_not_removed, self.store[:])
    
    def testSaveAndLoadAds(self):
        self.store.add_ads(self.some_ads)
        self.store.save()
        another_store = AdStore(self.path)
        first_ids = [ad.key for ad in self.some_ads]
        second_ids = [ad.key for ad in another_store]
        self.assertListEqual(first_ids, second_ids)

    def testSortByDate(self):
        delta = datetime.timedelta(hours = 2)
        for ad in self.some_ads:
            ad.timetag = datetime.datetime.now() + random.randint(0,20) * delta
        self.store.add_ads(self.some_ads)
        for i in range(1,self.store.length()):
            self.assertGreaterEqual(self.store[i].timetag, self.store[i-1].timetag)            

class TestAdAssessor(unittest.TestCase):
    
    def setUp(self):
        self.assessor = AdAssessor()
    
    def tearDown(self):pass
    
    def testAdCriterionPriceLimit(self):
        data = {"tag": "price", "limit": 50}
        priceCriterion = AdCriterionLimit(data)
        self.assessor.add_criterion(priceCriterion)
        ad = Ad({"price": 30})
        self.assertTrue(self.assessor.check(ad))
        ad = Ad({"price": 70})
        self.assertFalse(self.assessor.check(ad))

    def testAdCriterionTitleKeywordsAll(self):
        data = {"tag": "title", "keywords": ["schöner", "tag"]}
        kwdCriterion = AdCriterionKeywordsAll(data)
        self.assessor.add_criterion(kwdCriterion)
        ad = Ad({"title": "Das ist ein schöner Tag"})
        self.assertTrue(self.assessor.check(ad))
        ad = Ad({"title": "Das ist ein schöner Wagen"})
        self.assertFalse(self.assessor.check(ad))

    def testAdCriterionTitleKeywordsAny(self):
        data = {"tag": "title", "keywords": ["schöner", "tag"]}
        kwdCriterion = AdCriterionKeywordsAny(data)
        self.assessor.add_criterion(kwdCriterion)
        ad = Ad({"title": "Das ist ein schöner tag"})
        self.assertTrue(self.assessor.check(ad))
        ad = Ad({"title": "Das ist ein schöner Wagen"})
        self.assertTrue (self.assessor.check(ad))
        ad = Ad({"title": "Das ist ein schneller Wagen"})
        self.assertFalse(self.assessor.check(ad))
        
    def testAdCriterionTitleKeywordsNot(self):
        data = {"tag": "title", "keywords": ["schöner", "tag"]}
        kwdCriterion = AdCriterionKeywordsNot(data)
        self.assessor.add_criterion(kwdCriterion)
        ad = Ad({"title": "Das ist ein schöner tag"})
        self.assertFalse(self.assessor.check(ad))
        ad = Ad({"title": "Das ist ein schöner Wagen"})
        self.assertFalse (self.assessor.check(ad))
        ad = Ad({"title": "Das ist ein schneller Wagen"})
        self.assertTrue(self.assessor.check(ad))

    def testAdAssessorReturnsTrueWhenEmpty(self):
        ad = Ad(title = "Expensive Blablabla", price = 1e8)
        self.assertTrue (self.assessor.check(ad))

class TestLogger(unittest.TestCase):
    
    path = "./test.log"
    
    def setUp(self):
        self.logger = Logger(path = self.path, silent = True)
    
    def tearDown(self):
        os.remove(self.path)
    
    def testAppendLogEntry(self):
        s1 = "This is a test entry"
        s2 = "Another one!"
        self.logger.append(s1)
        with open(self.path, "r") as f:
            l = f.readline()
            self.assertRegex(l, s1)
        self.logger.append(s2)
        with open(self.path, "r") as f:
            l = f.readline()
            self.assertRegex(l, s1)
            l = f.readline()
            self.assertNotRegex(l, s1)
            self.assertRegex(l, s2)

class TestNotificationServer(unittest.TestCase):
    
    def setUp(self):
        self.notificationServer = NotificationServer()
    
    def tearDown(self):
        del self.notificationServer
    
    def testNotificationTypeError(self):
        x = 123
        self.assertRaises(TypeError, self.notificationServer.add_notification, x)
    
    def testAddDeleteNotificaions(self):
        a = Notification()
        b = Notification()
        self.notificationServer.add_notifications(a,b)
        self.assertIs(self.notificationServer[0], a)
        self.assertIs(self.notificationServer[1], b)
        self.assertRaises(IndexError, self.notificationServer.__getitem__, 2)
        del self.notificationServer[0]
        self.assertIs(self.notificationServer[0], b)        
        self.assertRaises(IndexError, self.notificationServer.__getitem__, 1)

class TestConnector(unittest.TestCase):
    
    def setUp(self):
        url = "http://www.willhaben.at/iad/kaufen-und-verkaufen/handy-organizer-telefon/handy-smartphone/"
        self.connector = Connector(url, "Willhaben")
    
    def tearDown(self):
        del self.connector
    
    def testAdsAfter(self):
        timelimit = datetime.datetime.now() - datetime.timedelta(hours = 1)
        ads = self.connector.ads_after(timelimit)
        for ad in ads:
            self.assertTrue(ad.timetag > timelimit)
    
    def testAdsIn(self):
        timedelta = datetime.timedelta(hours = 1)
        ads = self.connector.ads_in(timedelta)
        for ad in ads:
            self.assertTrue(ad.timetag > datetime.datetime.now()-timedelta)

class TestEmailNotification(unittest.TestCase):
    
    def setUp(self):
        with open("test.html", "r", encoding="UTF-8") as htmlfile:
            html = htmlfile.read()
        connector = Connector("http://example.com/", "Willhaben")
        self.ads = connector.__get_adlist_from_html__(html)

    def testMIMEStringGeneration(self):
        sender = "Gustl Hemmer <gustl@example.com>"
        to = "Moatl Hemmer <moatl@example.com>"
        mimetype = "text/plain"
        subject = "$Rückenschmerzen sind öfters schlächt$"
        body = "{datetime}{title}€{price}{url}"
        notification = EmailNotification(host = None, port = 25, user = None, 
                          pw = None, sender = sender, to = to, 
                          mimetype = mimetype, subject = subject, body = body)
        for ad in self.ads:
            notification._get_mail(ad, to)

if __name__ == "__main__":
    #unittest.main()
    test = TestEmailNotification()
    test.setUp()
    test.testMIMEStringGeneration()
