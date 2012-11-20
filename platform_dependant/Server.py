#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Server.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
from Notification import *
import smtplib

class EmailNotification(Notification):
	"""Sends email notification using python's smtplib module"""
	def __init__(self, host, port, user, pw, sender, to, mimetype, subject, body):
		self.host = host
		self.port = port
		self.user = user
		self.pw = pw
		self.sender = sender
		self.to = to
		self.subject = subject
		self.body = body
		self.headers = smtplib.email.mime.Text.MIMEText("", mimetype, "utf-8")
		self.headers["From"] = self.sender.encode("utf-8")
		self.headers["Subject"] = self.subject.encode("utf-8")

	def notify(self, ad):
		server = smtplib.SMTP(self.host, self.port)
		server.login(self.user, self.pw)
		for to in self.to:
			try:
				self.headers["To"] = to.encode("utf-8")
				msg = unicode(self.headers.as_string(), "utf-8") + self.body
				server.sendmail(self.sender, to, msg.format(**ad).encode("utf-8"))
			except KeyError as expn:
				raise NotificationError("Profile doesn't support tagname '{}'".format(expn.message))

