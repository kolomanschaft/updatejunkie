#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notification.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import smtplib
from email.mime.text import MIMEText

class NotificationError(Exception):pass

class Notification:
	def notify(self, ad):pass
	
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
		self.mimetype = mimetype
	
	def _get_mime_string(self, to, subject, body):
		mimetext = MIMEText(body.encode("utf-8"), self.mimetype, "utf-8")
		mimetext["From"] = self.sender.encode("utf-8")
		mimetext["Subject"] = subject.encode("utf-8")
		mimetext["To"] = to.encode("utf-8")
		return mimetext.as_string().encode("utf-8")


	def notify(self, ad):
		server = smtplib.SMTP(self.host, self.port)
		server.login(self.user, self.pw)
		for to in self.to:
			try:
				body = self.body.format(**ad)
				subject = self.subject.format(**ad)
				msg = self._get_mime_string(to, subject, body)
				server.sendmail(self.sender, to, msg)
			except KeyError as expn:
				raise NotificationError("Profile doesn't support tagname '{}'".format(expn.message))

