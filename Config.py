#!/usr/bin/env python
# encoding: utf-8
"""
Config.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
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
	def runmode(self):
		return self._parser.get("General", "runmode")
	
	@runmode.setter
	def runmode(self, mode):
		self._set("General", "runmode", mode)
	
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
	def update_interval(self):
		return self._parser.getint("General", "update.interval")

	@update_interval.setter
	def update_interval(self, interval):
		if not type(interval) is int:
			raise ConfigError("Update interval must be an integer number")
		self._set("General", "update.interval", str(interval))
		
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

	@title_keywords_any.setter
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
		self._parser.getint("PriceCriteria", "price.limit")

	@price_limit.setter
	def price_limit(self, price):
		if not type(price) is int:
			raise ConfigError("Price must be an integer number")
		self._set("PriceCriteria", "price.limit", str(price))

	@property
	def smtp_host(self):
		return self._parser.get("Email", "smtp.host")

	@smtp_host.setter
	def smtp_host(self, host):
		self._set("Email", "smtp.host", host)

	@property
	def smtp_port(self):
		return self._parser.get("Email", "smtp.port")

	@smtp_port.setter
	def smtp_port(self, port):
		self._set("Email", "smtp.port", port)

	@property
	def smtp_user(self):
		return self._parser.get("Email", "smtp.user")

	@smtp_user.setter
	def smtp_user(self, user):
		self._set("Email", "smtp.user", user)

	@property
	def smtp_pass(self):
		return self._parser.get("Email", "smtp.password")

	@smtp_pass.setter
	def smtp_pass(self, pw):
		self._set("Email", "smtp.password", pw)

	@property
	def email_from(self):
		return self._parser.get("Email", "address.from")

	@email_from.setter
	def email_from(self, sender):
		self._set("Email", "address.from", sender)

	@property
	def email_to(self):
		return self._parser.get("Email", "address.to")

	@email_to.setter
	def email_to(self, to):
		self._set("Email", "address.to", to)

	@property
	def email_subject(self):
		return self._parser.get("Email", "subject")

	@email_subject.setter
	def email_subject(self, subject):
		self._set("Email", "subject", subject)

	@property
	def email_body(self):
		return self._parser.get("Email", "body")

	@email_body.setter
	def email_body(self, body):
		self._set("Email", "body", body)

if __name__ == '__main__':
	
	# create test config
	
	path = "./files/test.cfg"
	with open(path, "w"): pass
	c = Config(path)
	
	c.runmode = "auto"
	c.url = "http://www.example.com/"
	c.ads_store = True
	c.title_keywords_all = ["word-1", "word-2"]
	c.title_keywords_any = ["word-3", "word-4", "word-5"]
	c.title_keywords_not = ["bad-word-1", "bad-word-2"]
	c.price_limit = 520
	c.update_interval = 66
	
	c.smtp_host = "bsmtp.telekom.at"
	c.smtp_port = "25"
	c.smtp_user = "martin@hammerschmied.at"
	c.smtp_pass = "l/1py78f"
	c.email_from = "Moatl<moatl@marvelous.at>"
	c.email_to = "Martin Hammerschmied<gestatten@gmail.com>"
	c.email_subject = "New Ad {0} for {2}"
	c.email_body = "Hello there!\n\nI found a new ad! The title is\n\n\"{0}\"\n\nand the price is {2}\n\nLink: {1}\n\nbye!"
	
	c.save()
	