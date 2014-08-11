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


class AdCriterion(object):
    def __init__(self, data):
        self._tagname = ""

    @property
    def tagname(self):
        return self._tagname

    def serialize(self):
        return {"tag": self._tagname}

    def check(self, ad):
        raise NotImplementedError("AdCriterion has to be subclassed.")
    
    @classmethod
    def from_json(cls, data):
        for subclass in AdCriterion.__subclasses__():
            if subclass.criterion_type == data["type"]:
                return subclass(data)


class AdCriterionLessThan(AdCriterion):
    criterion_type = "less_than"

    def __init__(self, data):
        self._tagname = data["tag"]
        self._limit = data["limit"]
    
    def check(self, ad):
        if self._limit >= ad[self._tagname]:
            return True
        else:
            return False

    def serialize(self):
        d = super(AdCriterionLessThan, self).serialize()
        d["type"] = self.criterion_type
        d["limit"] = self._limit
        return d


class AdCriterionGreaterThan(AdCriterion):
    criterion_type = "greater_than"

    def __init__(self, data):
        self._tagname = data["tag"]
        self._limit = data["limit"]
    
    def check(self, ad):
        if self._limit <= ad[self._tagname]:
            return True
        else:
            return False

    def serialize(self):
        d = super(AdCriterionGreaterThan, self).serialize()
        d["type"] = self.criterion_type
        d["limit"] = self._limit
        return d


class AdCriterionKeywordsAll(AdCriterion):
    criterion_type = "keywords_all"

    def __init__(self, data):
        self._tagname = data["tag"]
        self._keywords = data["keywords"]
    
    def check(self, ad):
        for kwd in self._keywords:
            if ad[self._tagname].lower().find(kwd.lower()) < 0:
                return False
        return True

    def serialize(self):
        d = super(AdCriterionKeywordsAll, self).serialize()
        d["type"] = self.criterion_type
        d["keywords"] = self._keywords
        return d


class AdCriterionKeywordsAny(AdCriterion):
    criterion_type = "keywords_any"

    def __init__(self, data):
        self._tagname = data["tag"]
        self._keywords = data["keywords"]

    def check(self, ad):
        for kwd in self._keywords:
            if ad[self._tagname].lower().find(kwd.lower()) >= 0:
                return True
        return False

    def serialize(self):
        d = super(AdCriterionKeywordsAny, self).serialize()
        d["type"] = self.criterion_type
        d["keywords"] = self._keywords
        return d


class AdCriterionKeywordsNot(AdCriterion):
    criterion_type = "keywords_not"

    def __init__(self, data):
        self._tagname = data["tag"]
        self._keywords = data["keywords"]

    def check(self, ad):
        for kwd in self._keywords:
            if ad[self._tagname].lower().find(kwd.lower()) >= 0:
                return False
        return True

    def serialize(self):
        d = super(AdCriterionKeywordsNot, self).serialize()
        d["type"] = self.criterion_type
        d["keywords"] = self._keywords
        return d


class AdAssessor:
    
    def __init__(self):
        self._criteria = []
    
    def add_criterion(self, criterion):
        if not isinstance(criterion, AdCriterion):
            raise TypeError("Expected type AdCriterion. Got {}".format(type(criterion)))
        self._criteria.append(criterion)
    
    def add_criteria(self, *args):
        for arg in args:
            self.add_criterion(arg)
            
    @property
    def criteria(self):
        return self._criteria
    
    def check(self, ad):
        return all([criterion.check(ad) for criterion in self._criteria])

