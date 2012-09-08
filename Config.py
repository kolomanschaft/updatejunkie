# -*- coding: utf-8 -*-
import ConfigParser
import os

class ConfigError(Exception): pass

class Config(object):
	
	def __init__(self, path):
		self.path = path
		self._parser = ConfigParser.SafeConfigParser()
		self.load()
	
	def save(self):
		with open(self.path, "w") as cfg:
			self._parser.write(cfg)
	
	def load(self):
		if os.path.exists(self.path):
			self._parser.read(self.path)
		else:
			raise ConfigError("Config file '{}' does not exist".format(self.path))
	
	def _probe_section(self, section):
		if not self._parser.has_section(section):
			self._parser.add_section(section)
	
	def _set(self, section, option, value):
		self._probe_section(section)
		self._parser.set(section, option, value)

	# The actual config options
	# -------------------------
	
	@property
	def url(self):
		return self._parser.get("General", "url")
	
	@url.setter
	def url(self, url):
		self._set("General", "url", url)

	@property
	def ads_store(self):
		return self._parser.getboolean("General", "ads.store")
	
	@ads_store.setter
	def ads_store(self, value):
		if value:
			self._set("General", "ads.store", "yes")
	
	@property
	def title_keywords_all(self):
		return eval(self._parser.get("TitleCriteria", "keywords.all"))
	
	@title_keywords_all.setter
	def title_keywords_all(self, kwds):
		if not type(kwds) is list: 
			raise ConfigError("Keywords argument must be a list")
		self._set("TitleCriteria", "keywords.all", str(kwds))

	@property
	def title_keywords_any(self):
		return eval(self._parser.get("TitleCriteria", "keywords.any"))

	@title_keywords_all.setter
	def title_keywords_any(self, kwds):
		if not type(kwds) is list: 
			raise ConfigError("Keywords argument must be a list")
		self._set("TitleCriteria", "keywords.any", str(kwds))

	@property
	def title_keywords_not(self):
		return eval(self._parser.get("TitleCriteria", "keywords.not"))

	@title_keywords_not.setter
	def title_keywords_not(self, kwds):
		if not type(kwds) is list: 
			raise ConfigError("Keywords argument must be a list")
		self._set("TitleCriteria", "keywords.not", str(kwds))
	
	@property
	def price_limit(self):
		self._parser.getint("TitleCriteria", "price.limit")

	@price_limit.setter
	def price_limit(self, price):
		if not type(price) is int:
			raise ConfigError("Price must be an integer number")
		self._set("TitleCriteria", "price.limit", str(price))
			
if __name__ == '__main__':
	
	# create default config
	
	path = "./files/sample.cfg"
	with open(path, "w"): pass
	c = Config(path)
	
	c.url = "http://www.example.com/"
	c.ads_store = True
	c.title_keywords_all = ["word-1", "word-2"]
	c.title_keywords_any = ["word-3", "word-4", "word-5"]
	c.title_keywords_not = ["bad-word-1", "bad-word-2"]
	c.price_limit = 520
	
	c.save()
	