#!/usr/bin/env python
# encoding: utf-8
"""
unittests.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import unittest
import os
from AdStore import *
from AdAssessor import *
from Logger import *
from Config import *

class TestAdStore(unittest.TestCase):
	
	path = "./testStore.save"
	
	def setUp(self):
		self.store = AdStore(self.path, flag = "n")
		
	def tearDown(self):
		os.remove(self.path)
		
	def testAddAndRemoveAds(self):
		some_ads = [Ad(title = "Ad " + str(nr), aid = nr) for nr in range(10)]
		added_ads = self.store.add_ads(some_ads)
		self.assertListEqual(some_ads, added_ads)
		ridx = [2,3,5,6,8]
		ads_to_remove = [some_ads[i] for i in ridx]
		removed = self.store.remove_ads(ads_to_remove)
		self.assertListEqual(ads_to_remove, removed)
		ads_not_removed = [ad for ad in some_ads if ad["id"] not in ridx]
		self.assertListEqual(ads_not_removed, self.store[:])
	
	def testSaveAndLoadAds(self):
		some_ads = [Ad(title = "Ad " + str(nr), aid = nr) for nr in range(10)]
		self.store.add_ads(some_ads)
		self.store.save()
		another_store = AdStore(self.path, flag = "r")
		first_ids = [ad["id"] for ad in some_ads]
		second_ids = [ad["id"] for ad in another_store]
		self.assertListEqual(first_ids, second_ids)

class TestAdAssessor(unittest.TestCase):
	
	def setUp(self):
		self.assessor = AdAssessor()
	
	def tearDown(self):pass
	
	def testAdCriterionPriceLimit(self):
		priceCriterion = AdCriterionPriceLimit(50)
		self.assessor.add_criterion(priceCriterion)
		ad = Ad(price = 30)
		self.assertTrue(self.assessor.check(ad))
		ad = Ad(price = 72)
		self.assertFalse(self.assessor.check(ad))

	def testAdCriterionTitleKeywordsAll(self):
		kwdCriterion = AdCriterionTitleKeywordsAll([u"schöner", u"tag"])
		self.assessor.add_criterion(kwdCriterion)
		ad = Ad(title = u"Das ist ein schöner Tag")
		self.assertTrue(self.assessor.check(ad))
		ad = Ad(title = u"Das ist ein schöner Wagen")
		self.assertFalse(self.assessor.check(ad))

	def testAdCriterionTitleKeywordsAny(self):
		kwdCriterion = AdCriterionTitleKeywordsAny([u"schöner", u"tag"])
		self.assessor.add_criterion(kwdCriterion)
		ad = Ad(title = u"Das ist ein schöner tag")
		self.assertTrue(self.assessor.check(ad))
		ad = Ad(title = u"Das ist ein schöner Wagen")
		self.assertTrue (self.assessor.check(ad))
		ad = Ad(title = u"Das ist ein schneller Wagen")
		self.assertFalse(self.assessor.check(ad))
		
	def testAdCriterionTitleKeywordsNot(self):
		kwdCriterion = AdCriterionTitleKeywordsNot([u"schöner", u"tag"])
		self.assessor.add_criterion(kwdCriterion)
		ad = Ad(title = u"Das ist ein schöner tag")
		self.assertFalse(self.assessor.check(ad))
		ad = Ad(title = u"Das ist ein schöner Wagen")
		self.assertFalse (self.assessor.check(ad))
		ad = Ad(title = u"Das ist ein schneller Wagen")
		self.assertTrue(self.assessor.check(ad))

	def testAdAssessorReturnsTrueWhenEmpty(self):
		ad = Ad(title = u"Expensive Blablabla", price = 1e8)
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
			self.assertRegexpMatches(l, s1)
		self.logger.append(s2)
		with open(self.path, "r") as f:
			l = f.readline()
			self.assertRegexpMatches(l, s1)
			l = f.readline()
			self.assertNotRegexpMatches(l, s1)
			self.assertRegexpMatches(l, s2)

class TestConfig(unittest.TestCase):
	
	path = "./test.cfg"
	
	def setUp(self):
		if not os.path.exists(self.path):
			f = open(self.path, "w")
			f.close()
		self.config = Config(self.path)
	
	def tearDown(self):
		os.remove(self.path)
	
	def testSafeLoadOptions(self):
		testurl = "http://example.com"
		self.config.url = testurl
		self.config.save()
		c = Config(self.path)
		self.assertTrue(testurl == c.url)
	
	def testSaveLoadCriteria(self):
		kwds = ["word-1", "word-2", "word-3"]
		self.config.title_keywords_all = kwds
		self.config.save()
		c = Config(self.path)
		self.assertListEqual(kwds, c.title_keywords_all)

if __name__ == "__main__":
	unittest.main()