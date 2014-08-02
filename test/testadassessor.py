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
        self._assessor = AdAssessor()
        self._base_ad = Ad({"id":1, "dt":"2014-07-07"}, "id", "dt")

    def tearDown(self):pass
    
    def test_ad_criterion_less_than(self):
        data = {"tag": "price", "limit": 50}
        priceCriterion = AdCriterionLessThan(data)
        self._assessor.add_criterion(priceCriterion)
        self._base_ad["price"] = 30
        self.assertTrue(self._assessor.check(self._base_ad))
        self._base_ad["price"] = 70
        self.assertFalse(self._assessor.check(self._base_ad))

    def test_ad_criterion_greater_than(self):
        data = {"tag": "price", "limit": 50}
        priceCriterion = AdCriterionGreaterThan(data)
        self._assessor.add_criterion(priceCriterion)
        self._base_ad["price"] = 30
        self.assertFalse(self._assessor.check(self._base_ad))
        self._base_ad["price"] = 70
        self.assertTrue(self._assessor.check(self._base_ad))

    def test_ad_criterion_title_keywords_all(self):
        data = {"tag": "title", "keywords": ["schöner", "tag"]}
        kwdCriterion = AdCriterionKeywordsAll(data)
        self._assessor.add_criterion(kwdCriterion)
        self._base_ad["title"] = "Das ist ein schöner Tag"
        self.assertTrue(self._assessor.check(self._base_ad))
        self._base_ad["title"] = "Das ist ein schöner Wagen"
        self.assertFalse(self._assessor.check(self._base_ad))

    def test_ad_criterion_title_keywords_any(self):
        data = {"tag": "title", "keywords": ["schöner", "tag"]}
        kwdCriterion = AdCriterionKeywordsAny(data)
        self._assessor.add_criterion(kwdCriterion)
        self._base_ad["title"] = "Das ist ein schöner tag"
        self.assertTrue(self._assessor.check(self._base_ad))
        self._base_ad["title"] = "Das ist ein schöner Wagen"
        self.assertTrue (self._assessor.check(self._base_ad))
        self._base_ad["title"] = "Das ist ein schneller Wagen"
        self.assertFalse(self._assessor.check(self._base_ad))
        
    def test_ad_criterion_title_keywords_not(self):
        data = {"tag": "title", "keywords": ["schöner", "tag"]}
        kwdCriterion = AdCriterionKeywordsNot(data)
        self._assessor.add_criterion(kwdCriterion)
        self._base_ad["title"] = "Das ist ein schöner tag"
        self.assertFalse(self._assessor.check(self._base_ad))
        self._base_ad["title"] = "Das ist ein schöner Wagen"
        self.assertFalse (self._assessor.check(self._base_ad))
        self._base_ad["title"] = "Das ist ein schneller Wagen"
        self.assertTrue(self._assessor.check(self._base_ad))

    def test_adassessor_returns_true_if_empty(self):
        self._base_ad["title"] = "Expensive Blablabla"
        self.assertTrue (self._assessor.check(self._base_ad))