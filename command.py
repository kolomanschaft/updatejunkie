#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command.py

Created by Martin Hammerschmied on 2013-10-25.
Copyright (c) 2013. All rights reserved.
"""

from Profile import get_profile
from AdStore import AdStore
from AdAssessor import AdAssessor, AdCriterion
from NotificationServer import NotificationServer
from Observer import Observer


class CommandError(Exception):pass


class Command(object):
    """
    Base class for all commands.
    """

    def __init__(self, server, json_decoded):
        self._server = server
        self._json_decoded = json_decoded
    
    def execute(self):
        raise CommandError("Execute must be implemented in a subclass.")
    
    @classmethod
    def from_json(cls, server, json_decoded):
        if ("command" not in json_decoded):
            raise CommandError("The given data is not a valid command.")

        for cmd in Command.__subclasses__():
            if cmd.name == json_decoded["command"]:
                return cmd(server, json_decoded)
        
        raise CommandError("Unknown command: {}".format(json_decoded["command"]))


class SmtpSettingsCommand(Command):
    """
    Command to change the SMTP settings for sending email notifications.
    """
    name = "smtp_config"
    
    def execute(self):
        self.validate_smtp_config(self._json_decoded)
        if "user" not in self._json_decoded:
            self._json_decoded["user"] = None
        if "pass" not in self._json_decoded:
            self._json_decoded["pass"] = None
        self._server.config["smtp"] = self._json_decoded
    
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
        self._server._logger.append("Setting up observer " + self._json_decoded["name"])
        profile = get_profile(self._json_decoded["profile"])
        store = self._setup_store()
        
        
        assessor = AdAssessor()
        for json in self._json_decoded["criteria"]:
            assessor.add_criterion(AdCriterion.from_json(json))
     
        # Notification server setup
        notificationServer = NotificationServer()
        for json in self._json_decoded["notifications"]:
            notification = self._setup_notification(json, profile)
            notificationServer.add_notification(notification)

        # Setup the actual observer
        observer = Observer(url = self._json_decoded["url"], profile = profile,
                            store = store, assessor = assessor,
                            notifications = notificationServer,
                            logger = self._server.logger,
                            update_interval = self._json_decoded["interval"],
                            name = self._json_decoded["name"])
        
        self._server.add_observer(observer)

    def _setup_store(self):
        save_file = None    # Ads that have already been processed are registered in this file
        if self._json_decoded["store"] == True:
            save_file = "files/adstore.{}.db".format(self._json_decoded["name"])
        else: 
            save_file = None    
        return AdStore(path = save_file)
    
    def _setup_notification(self, json, profile):
        if (json["type"] == "email"):
            if not self._server.config["smtp"]:
                raise CommandError("Cannot setup email notifications without smtp settings.")

            from platform_dependant.Notification import EmailNotification
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
        if "name" not in self._json_decoded:
            raise CommandError("The remove_observer command must specify a name.")
        self._server.remove_observer(self._json_decoded["name"])


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
        if "name" not in self._json_decoded:
            raise CommandError("The get_observer command must specify a name.")
        observer = self._server[self._json_decoded["name"]]
        if observer is None:
            raise CommandError("Observer {} not found.".format(self._json_decoded["name"]))
        return observer.serialize()


class ListCommandsCommand(Command):
    """
    Returns a list of all available commands.
    """
    name = "list_commands"
    
    def execute(self):
        return [cmd_class.command for cmd_class in Command.__subclasses__()]

