# -*- coding: utf-8 -*-
import shelve

class Ad:
	
	def __init__(self, aid = None, title = None, url = None, price = None):
		self.id = aid
		self.title = title
		self.url = url
		self.price = price
	
	def __getitem__(self, key):
		if key == "id":
			return self.id
		elif key == "title":
			return self.title
		elif key == "url":
			return self.url
		elif key == "price":
			return self.price

	def __setitem__(self, key, value):
		if key == "id":
			self.id = value
		elif key == "title":
			self.title = value
		elif key == "url":
			self.url = value
		elif key == "price":
			self.price = value
	
	def __repr__(self):
		s = "\nAd(aid = \"{0}\",\n   title = \"{1}\",\n   url = \"{2}\",\n   price = \"{3}\")"
		return s.format(self.id, self.title, self.url, self.price)

class AdStore:
	
	def __init__(self, path = None, flag = "c", autosave = True):
		"""
		'flag' has the same meaning as the 'flag' parameter in anydbm.open()
		"""
		if path == None:
			self.path = "./adstore.save"
		else:
			self.path = path
		self.flag = flag
		self.autosave = autosave
		self.load()
	
	def save(self):
		sh = shelve.open(self.path, self.flag)
		try:
			sh["ads"] = self.ads
		finally:
			sh.close()
		return True
	
	def load(self):
		sh = shelve.open(self.path, self.flag)
		try:
			self.ads = sh["ads"]
		except KeyError:
			self.ads = []
		finally:
			sh.close()
	
	def add_ads(self, ads):
		"""
		'ads' is a list of new ads
		"""
		added_ads = []
		cur_ids = [ad["id"] for ad in self.ads]
		new_ids = [ad["id"] for ad in ads]
		for i in range(len(new_ids)):
			if new_ids[i] not in cur_ids:
				self.ads.append(ads[i])
				added_ads.append(ads[i])
		if self.autosave: self.save()
		return added_ads
	
	def remove_ads(self, ads):
		removed_ads = []
		cur_ids = [ad["id"] for ad in self.ads]
		new_ids = [ad["id"] for ad in ads]
		for i in range(len(new_ids)):
			if new_ids[i] in cur_ids:
				idx = cur_ids.index(new_ids[i])
				del self.ads[idx]
				del cur_ids[idx]
				removed_ads.append(ads[i])
		if self.autosave: self.save()
		return removed_ads
	
	def __getitem__(self, key):
		return self.ads[key]