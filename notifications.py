#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2012 Martin Hammerschmied

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import smtplib
import re
import logging

from email.mime.text import MIMEText
from email.header import Header


class NotificationError(Exception):pass


class Notification:
    def notify(self, ad):
        raise NotImplementedError("notify() must be implemented in subclass.")
    
    def serialize(self):
        raise NotImplementedError("serialize() must be implemented in subclass.")
    
    
class EmailNotification(Notification):
    """
    Sends email notification using python's smtplib module
    """

    def __init__(self, host, port, sender, to, subject, body, auth=False, user=None, pwd=None, mimetype="text/plain"):
        self._host = host
        self._port = port
        self._auth = auth
        self._user = user
        self._pwd = pwd
        self._sender = sender
        self._to = to
        self._subject = subject
        self._body = body
        self._mimetype = mimetype

    def _get_mime_string(self, to, subject, body):
        match = re.match("text/(.+)", self._mimetype)
        if not match:
            raise RuntimeError("MIME type not supported: {}".format(self._mimetype))
        subtype = match.groups()[0]
        mimetext = MIMEText(body, subtype, _charset = "utf-8")
        mimetext["From"] = self._sender
        mimetext["Subject"] = Header(subject, "utf-8")
        mimetext["To"] = Header(to, "utf-8")
        return mimetext.as_string()
    
    def _get_mail(self, ad, to):
        try:
            body = self._body.format(**ad)
            subject = self._subject.format(**ad)
            msg = self._get_mime_string(to, subject, body)
        except KeyError as expn:
            raise NotificationError("Profile doesn't support tagname '{}'".format(expn.args[0]))
        return msg

    def notify(self, ad):
        server = None
        try:
            server = smtplib.SMTP(self._host, self._port)
            try:
                server.starttls()
            except smtplib.SMTPException:
                logging.debug("The SMTP server does not support STARTTLS")
            if self._auth:
                server.login(self._user, self._pwd)
            for to in self._to:
                msg = self._get_mail(ad, to)
                logging.debug("Sending mail to {}".format(to))
                server.sendmail(self._sender, to, msg)
        except smtplib.SMTPAuthenticationError as error:
            logging.error("SMTP Authentication failed: {}".format(error.args))
        except ConnectionRefusedError:
            logging.error("Connection to {} was refused!".format(self._host))
        except Exception as error:
            logging.error("Failed to send email notification: {}".format(error.args))
        finally:
            if server: server.quit()

    def serialize(self):
        return {"type": "email", "to": self._to}
