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

from profile import get_profile
from adstore import AdStore
from adassessor import AdAssessor, AdCriterion
from notificationserver import NotificationServer
from observer import Observer
from threading import Condition

import os
import logging

class CommandError(Exception):pass


class Command(object):
    """
    Base class for all commands.
    """

    def __init__(self, cmd_info, server = None):
        self._cmd_info = cmd_info
        self._server = server
        self._cv = Condition()
        self._result = None
    
    def execute(self):
        raise CommandError("Execute must be implemented in a subclass.")
    
    @classmethod
    def from_command_info(cls, cmd_info):
        if ("command" not in cmd_info):
            raise CommandError("The given data is not a valid command.")

        for cmd in Command.__subclasses__():
            if cmd.name == cmd_info["command"]:
                return cmd(cmd_info)
        
        raise CommandError("Unknown command: {}".format(cmd_info["command"]))
    
    @property
    def server(self):
        """
        The server to execute the command on.
        """
        return self._server
    
    @server.setter
    def server(self, server):
        self._server = server
        
    @property
    def condition(self):
        """
        A condition variable which will be notified after the command was 
        executed by the server. The result will also be available at the 
        time of notification.
        """
        return self._cv
    
    @property
    def result(self):
        """
        After the command was executed the server stores the result in 
        this property.
        """
        return self._result
    
    @result.setter
    def result(self, result):
        self._result = result


class SmtpSettingsCommand(Command):
    """
    Command to change the SMTP settings for sending email notifications.
    """
    name = "smtp_config"
    
    def execute(self):
        self.validate_smtp_config(self._cmd_info)
        if "user" not in self._cmd_info:
            self._cmd_info["user"] = None
        if "pass" not in self._cmd_info:
            self._cmd_info["pass"] = None
        self._server.config["smtp"] = self._cmd_info
    
    def validate_smtp_config(self, config):
        if ("host" not in config):
            raise CommandError("'host' is missing in the smtp configuration.")
        if ("port" not in config):
            raise CommandError("'port' is missing in the smtp configuration.")


class NewObserverCommand(Command):
    """
    Setup a new observer. If an older observer is running with the same name, 
    it will be replaced by the new observer.
    """
    name = "new_observer"

    def execute(self):
        logging.info("Setting up observer " + self._cmd_info["name"])
        profile = get_profile(self._cmd_info["profile"])
        store = self._setup_store()
        
        assessor = AdAssessor()
        for json in self._cmd_info["criteria"]:
            assessor.add_criterion(AdCriterion.from_json(json))
     
        # Notification server setup
        notificationServer = NotificationServer()
        for json in self._cmd_info["notifications"]:
            notification = self._setup_notification(json, profile)
            notificationServer.add_notification(notification)

        # Setup the actual observer
        observer = Observer(url = self._cmd_info["url"], profile = profile,
                            store = store, assessor = assessor,
                            notifications = notificationServer,
                            update_interval = self._cmd_info["interval"],
                            name = self._cmd_info["name"])
        
        self._server.add_observer(observer)

    def _setup_store(self):
        save_file = None    # Ads that have already been processed are registered in this file
        if self._cmd_info["store"] == True:
            if not os.path.exists("./store/"): os.mkdir("store")
            save_file = "store/adstore.{}.db".format(self._cmd_info["name"])
        return AdStore(path = save_file)
    
    def _setup_notification(self, json, profile):
        if (json["type"] == "email"):
            if not self._server.config["smtp"]:
                raise CommandError("Cannot setup email notifications without smtp settings.")

            from notifications import EmailNotification
            formatting = profile.Notifications.Email
            smtp = self._server.config["smtp"]
            to = json["to"]
            if (type(to) == str):
                to = [to]   # make it a list
            email_notification = EmailNotification(smtp["host"], smtp["port"],
                                                   smtp["user"], smtp["pass"],
                                                   formatting.From, json["to"],
                                                   formatting.ContentType,
                                                   formatting.Subject,
                                                   formatting.Body.valueOf_)
            return email_notification
        
        
class RemoveObserverCommand(Command):
    """
    Command to remove an observer by its name.
    """
    name = "remove_observer"
    
    def execute(self):
        if "name" not in self._cmd_info:
            raise CommandError("The remove_observer command must specify a name.")
        self._server.remove_observer(self._cmd_info["name"])


class ListObserversCommand(Command):
    """
    Returns a list of all observers that are currently running.
    """
    name = "list_observers"
    
    def execute(self):
        return [observer.name for observer in self._server]


class GetObserverCommand(Command):
    """
    Returns a list of all observers that are currently running.
    """
    name = "get_observer"
    
    def execute(self):
        if "name" not in self._cmd_info:
            raise CommandError("The get_observer command must specify a name.")
        observer = self._server[self._cmd_info["name"]]
        if observer is None:
            raise CommandError("Observer {} not found.".format(self._cmd_info["name"]))
        return observer.serialize()


class ListCommandsCommand(Command):
    """
    Returns a list of all available commands.
    """
    name = "list_commands"
    
    def execute(self):
        return [cmd_class.command for cmd_class in Command.__subclasses__()]

