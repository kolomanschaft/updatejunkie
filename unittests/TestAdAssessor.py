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

import unittest
from adassessor import *
from connector import *


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