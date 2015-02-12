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

import profiles
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
        self._response = None
    
    def execute(self):
        raise CommandError("Execute must be implemented in a subclass.")
    
    @classmethod
    def from_command_info(cls, cmd_info):
        if type(cmd_info) != dict or "command" not in cmd_info:
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
        executed by the server. The response will also be available at the 
        time of notification.
        """
        return self._cv
    
    @property
    def response(self):
        """
        After the command was executed the server stores the response in 
        this property.
        """
        return self._response
    
    @response.setter
    def response(self, response):
        self._response = response


class SmtpSettingsCommand(Command):
    """
    Command to change the SMTP settings for sending email notifications.
    """
    name = "smtp_settings"
    
    def execute(self):
        smtp_settings = self._cmd_info
        smtp_settings.pop("command")
        self._validate_smtp_settings(smtp_settings)
        if "user" not in smtp_settings:
            smtp_settings["user"] = None
        if "pwd" not in smtp_settings:
            smtp_settings["pwd"] = None
        self._server.settings["smtp"] = smtp_settings
    
    def _validate_smtp_settings(self, settings):
        if "host" not in settings:
            raise CommandError("'host' is missing in the smtp settings.")
        if "port" not in settings:
            raise CommandError("'port' is missing in the smtp settings.")


class CreateObserverCommand(Command):
    """
    Create and setup a new observer. If an older observer is running with the 
    same name, it will be replaced by the new observer.
    """
    name = "create_observer"

    def execute(self):
        logging.info("Setting up observer '{}'".format(self._cmd_info["name"]))
        profile = profiles.get_profile_by_name(self._cmd_info["profile"])
        store = None
        if self._cmd_info["store"]:
            store = self._setup_store()
        assessor = AdAssessor()
        for json in self._cmd_info["criteria"]:
            assessor.add_criterion(AdCriterion.from_json(json))
        notification_server = NotificationServer()  # Add an empty notification server
        observer = Observer(url=self._cmd_info["url"], profile=profile, # Setup the actual observer
                            store=store, assessor=assessor,
                            notifications=notification_server,
                            update_interval=self._cmd_info["interval"],
                            name=self._cmd_info["name"])
        
        self._server.add_observer(observer)

    def _setup_store(self):
        save_file = None    # Ads that have already been processed are registered in this file
        if self._cmd_info["store"]:
            if not os.path.exists("./store/"): os.mkdir("store")
            save_file = "store/adstore.{}.db".format(self._cmd_info["name"])
        return AdStore(path=save_file)


class AddNotificationCommand(Command):
    """
    Adds a new notification and associates it with a running observer.
    """
    name = "add_notification"

    def execute(self):
        notification_type = self._cmd_info["type"]
        observer_name = self._cmd_info["observer"]
        logging.info("Adding {} notification to observer '{}'".format(notification_type, observer_name))
        notification = None
        if notification_type == "email":
            notification = self._setup_email_notification()
        self._server[observer_name].notifications.add_notification(notification)

    def _setup_email_notification(self):
        if not "smtp" in self._server.settings.keys():
            raise CommandError("Cannot setup email notifications without smtp settings.")
        header_from = self._cmd_info["from"]
        header_to = self._cmd_info["to"]
        header_mime_type = self._cmd_info["mime_type"]
        header_subject = self._cmd_info["subject"]
        body = self._cmd_info["body"]
        smtp = self._server.settings["smtp"]
        if type(header_to) == str:
            header_to = [header_to]   # make it a list

        from notifications import EmailNotification
        email_notification = EmailNotification(smtp["host"], smtp["port"],
                                               smtp["user"], smtp["pwd"],
                                               header_from, header_to,
                                               header_mime_type,
                                               header_subject, body)
        return email_notification


class PauseObserverCommand(Command):
    """
    Pauses an observer
    """
    name = "pause_observer"

    def execute(self):
        if "name" not in self._cmd_info:
            raise CommandError("The pause_observer command must specify a name.")
        try:
            self._server[self._cmd_info["name"]].state = Observer.PAUSED
        except KeyError as error:
            raise CommandError(error.args[0])


class ResumeObserverCommand(Command):
    """
    Resumes a paused observer
    """
    name = "resume_observer"

    def execute(self):
        if "name" not in self._cmd_info:
            raise CommandError("The pause_observer command must specify a name.")
        try:
            self._server[self._cmd_info["name"]].state = Observer.RUNNING
        except KeyError as error:
            raise CommandError(error.args[0])


class RemoveObserverCommand(Command):
    """
    Remove an observer
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
        return [{"name": observer.name,
                 "state": observer.state
                }
                for observer in self._server]


class GetObserverCommand(Command):
    """
    Returns a list of all observers that are currently running.
    """
    name = "get_observer"
    
    def execute(self):
        if "name" not in self._cmd_info:
            raise CommandError("The get_observer command must specify a name.")
        try:
            observer = self._server[self._cmd_info["name"]]
            return observer.serialize()
        except KeyError as error:
            raise CommandError(error.args[0])


class ListCommandsCommand(Command):
    """
    Returns a list of all available commands.
    """
    name = "list_commands"
    
    def execute(self):
        return [cmd_class.name for cmd_class in Command.__subclasses__()]


class WebSettingsCommand(Command):
    """
    Configure the web API. After this command the web API will be restarted.
    FIXME: How could this be made available over the web API itself?
    """
    name = "web_settings"

    def execute(self):
        if not "host" in self._cmd_info:
            raise CommandError("Command info is missing host information")
        if not "port" in self._cmd_info:
            raise CommandError("Command info is missing port information")
        web_settings = dict(host=self._cmd_info["host"],
                            port=self._cmd_info["port"])
        self._server.settings["web"] = web_settings