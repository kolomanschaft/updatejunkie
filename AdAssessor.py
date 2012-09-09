#!/usr/bin/env python
# encoding: utf-8
"""
AdAssessor.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""

class AdCriterion:
	def check(self,add): return True

class AdCriterionPriceLimit(AdCriterion):
	
	def __init__(self, pricelimit):
		self.pricelimit = pricelimit
	
	def check(self, ad):
		if self.pricelimit >= ad["price"]:
			return True
		else:
			return False

class AdCriterionTitleKeywordsAll(AdCriterion):
	
	def __init__(self, keywords):
		self.keywords = keywords
	
	def check(self, ad):
		for kwd in self.keywords:
			if ad["title"].lower().find(kwd.lower()) < 0:
				return False
		return True

class AdCriterionTitleKeywordsAny(AdCriterion):

	def __init__(self, keywords):
		self.keywords = keywords

	def check(self, ad):
		for kwd in self.keywords:
			if ad["title"].lower().find(kwd.lower()) >= 0:
				return True
		return False

class AdCriterionTitleKeywordsNot(AdCriterion):

	def __init__(self, keywords):
		self.keywords = keywords

	def check(self, ad):
		for kwd in self.keywords:
			if ad["title"].lower().find(kwd.lower()) >= 0:
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

