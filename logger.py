#!/usr/bin/env python3
# encoding: utf-8
"""
Logger.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import time
import codecs

class Logger:
	
	def __init__(self, path = None, silent = False):
		self.path = path
		self.silent = silent
	
	def append(self, msg):
		s = time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg
		if self.path:
			with codecs.open(self.path, mode = "a", encoding = "utf-8") as f:
				f.write(s + "\n")

		if not self.silent:
			print(s)