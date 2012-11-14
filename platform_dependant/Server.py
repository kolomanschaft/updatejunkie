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
	def __init__(self, host, port, user, pw, sender, to, subject, body):
		self.host = host
		self.port = port
		self.user = user
		self.pw = pw
		self.sender = sender
		self.to = to
		self.subject = subject
		MIMEHeader = smtplib.email.mime.Text.MIMEText("", "plain", "utf-8")
		MIMEHeader["From"] = self.sender.encode("utf-8")
		MIMEHeader["To"] = self.to.encode("utf-8")
		MIMEHeader["Subject"] = self.subject.encode("utf-8")
		self.msg = unicode(MIMEHeader.as_string(), "utf-8") + body

	def notify(self, ad):
		server = smtplib.SMTP(self.host, self.port)
		server.login(self.user, self.pw)
		server.sendmail(self.sender, self.to, self.msg.format(**ad).encode("utf-8"))

