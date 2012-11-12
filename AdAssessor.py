#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AdAssessor.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""

class AdCriterion(object):
    def __init__(self, tagname): 
        self._tagname = tagname

    def check(self, ad): return True

class AdCriterionLimit(AdCriterion):
    
    def __init__(self, tagname, limit):
        super(AdCriterionLimit, self).__init__(tagname)
        if not isinstance(limit, int):
            raise TypeError("Limit must be an integer!")
        self._limit = limit
    
    def check(self, ad):
        if self._limit >= ad[self._tagname]:
            return True
        else:
            return False

class AdCriterionKeywordsAll(AdCriterion):

    def __init__(self, tagname, keywords):
        super(AdCriterionKeywordsAll, self).__init__(tagname)
        if not isinstance(keywords, list):
            raise TypeError("Keywords must be a list!")
        self._keywords = [unicode(keyword) for keyword in keywords]
    
    def check(self, ad):
        for kwd in self._keywords:
            if ad[self._tagname].lower().find(kwd.lower()) < 0:
                return False
        return True

class AdCriterionKeywordsAny(AdCriterion):

    def __init__(self, tagname, keywords):
        super(AdCriterionKeywordsAny, self).__init__(tagname)
        if not isinstance(keywords, list):
            raise TypeError("Keywords must be a list!")
        self._keywords = [unicode(keyword) for keyword in keywords]

    def check(self, ad):
        for kwd in self._keywords:
            if ad[self._tagname].lower().find(kwd.lower()) >= 0:
                return True
        return False

class AdCriterionKeywordsNot(AdCriterion):

    def __init__(self, tagname, keywords):
        super(AdCriterionKeywordsNot, self).__init__(tagname)
        if not isinstance(keywords, list):
            TypeError("Keywords must be a list!")
        self._keywords = [unicode(keyword) for keyword in keywords]

    def check(self, ad):
        for kwd in self._keywords:
            if ad[self._tagname].lower().find(kwd.lower()) >= 0:
                return False
        return True

class AdAssessor:
    
    def __init__(self):
        self.criterions = []
    
    def add_criterion(self, criterion):
        if not isinstance(criterion, AdCriterion):
            raise TypeError("Expected type AdCriterion. Got {}".format(type(criterion)))
        self.criterions.append(criterion)
    
    def add_criteria(self, *args):
        for arg in args:
            self.add_criterion(arg)
    
    def check(self, ad):
        return all([criterion.check(ad) for criterion in self.criterions])

