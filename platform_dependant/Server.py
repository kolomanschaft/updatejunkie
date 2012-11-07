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
		MIMEHeader = smtplib.email.mime.Text.MIMEText("")
		MIMEHeader["From"] = self.sender
		MIMEHeader["To"] = self.to
		MIMEHeader["Subject"] = self.subject
		self.msg = MIMEHeader.as_string() + body

	def notify(self, ad):
		server = smtplib.SMTP(self.host, self.port)
		server.login(self.user, self.pw)
		server.sendmail(self.sender, self.to, self.msg.format(**ad).encode("utf-8"))

