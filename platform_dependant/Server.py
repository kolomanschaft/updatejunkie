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
		self.msg = unicode(MIMEHeader.as_string() + body)

	def notify(self, ad):
		server = smtplib.SMTP(self.host, self.port)
		server.login(self.user, self.pw)
		server.sendmail(self.sender, self.to, self.msg.format(**ad).encode("utf-8"))


if __name__ == '__main__':
	host = "bsmtp.telekom.at"
	port = "25"
	user = "martin@hammerschmied.at"
	pw = "l/1py78f"
	sender = "Moatl<moatl@marvelous.at>"
	to = "Martin Hammerschmied<gestatten@gmail.com>"
	subject = "New Ad {0} for {2}"
	body = "Hello there!\n\nI found a new ad! The title is\n\n\"{0}\"\n\nand the price is {2}\n\nLink: {1}\n\nbye!"
	
	notiication = EmailNotification(host, port, user, pw, sender, to, subject, body)
	notiication.notify("HANDY!!!", "€ 500", "", "http://www.hammerschmied.at/")