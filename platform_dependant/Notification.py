#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import smtplib
import re
from email.mime.text import MIMEText
from email.header import Header

class NotificationError(Exception):pass

class Notification:
	def notify(self, ad):pass
	
	def serialize(self):
		raise NotImplementedError("Notification must be subclassed.")
	
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
		match = re.match("text/(.+)", self.mimetype)
		if not match:
			raise RuntimeError("MIME type not supported: {}".format(self.mimetype))
		subtype = match.groups()[0]
		mimetext = MIMEText(body, subtype, _charset = "utf-8")
		mimetext["From"] = self.sender
		mimetext["Subject"] = Header(subject, "utf-8")
		mimetext["To"] = Header(to, "utf-8")
		return mimetext.as_string()
	
	def _get_mail(self, ad, to):
		try:
			body = self.body.format(**ad)
			subject = self.subject.format(**ad)
			msg = self._get_mime_string(to, subject, body)
		except KeyError as expn:
			raise NotificationError("Profile doesn't support tagname '{}'".format(expn.message))
		return msg


	def notify(self, ad):
		server = smtplib.SMTP(self.host, self.port)
		server.login(self.user, self.pw)
		for to in self.to:
			msg = self._get_mail(ad, to)
			server.sendmail(self.sender, to, msg)

	def serialize(self):
		return {"type": "email", "to": self.to}
