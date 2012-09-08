# -*- coding: utf-8 -*-	
import time

class Logger:
	
	def __init__(self, path = None, silent = False):
		self.path = path
		self.silent = silent
	
	def append(self, msg):
		s = time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg
		if self.path:
			with open(self.path, "a") as f:
				f.write(s + "\n")
		
		if not self.silent:
			print s