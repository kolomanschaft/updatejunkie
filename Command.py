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

    def __init__(self, server, data):
        self._server = server
        self._data = data
    
    def execute(self):
        raise CommandError("Execute must be implemented in a subclass.")
    
    @classmethod
    def from_json(cls, server, data):
        if ("command" not in data):
            raise CommandError("The given data is not a valid command.")

        for subclass in Command.__subclasses__():
            if subclass.command == data["command"]:
                return subclass(server, data)
                
#         # Dispatch the command
#         if (data["command"] == "new_observer"):
#             return NewObserverCommand(server, data)
#         elif (data["command"] == "remove_observer"):
#             return RemoveObserverCommand(server, data)
#         elif (data["command"] == "smtp_config"):
#             return SmtpSettingsCommand(server, data)
        
        raise CommandError("Unknown command: {}".format(data["command"]))


class SmtpSettingsCommand(Command):
    """
    Command to change the SMTP settings for sending email notifications.
    """
    command = "smtp_config"
    
    def execute(self):
        self.validate_smtp_config(self._data)
        if "user" not in self._data:
            self._data["user"] = None
        if "pass" not in self._data:
            self._data["pass"] = None
        self._server.config["smtp"] = self._data
    
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
    command = "new_observer"

    def execute(self):
        self._server._logger.append("Setting up observer " + self._data["name"])
        profile = get_profile(self._data["profile"])
        store = self._setup_store()
        
        
        assessor = AdAssessor()
        for json in self._data["criteria"]:
            assessor.add_criterion(AdCriterion.from_json(json))
     
        # Notification server setup
        notificationServer = NotificationServer()
        for json in self._data["notifications"]:
            notification = self._setup_notification(json, profile)
            notificationServer.add_notification(notification)

        # Setup the actual observer
        observer = Observer(url = self._data["url"], profile = profile,
                            store = store, assessor = assessor,
                            notifications = notificationServer,
                            logger = self._server.logger,
                            update_interval = self._data["interval"],
                            name = self._data["name"])
        
        self._server.add_observer(observer)

    def _setup_store(self):
        save_file = None    # Ads that have already been processed are registered in this file
        if self._data["store"] == True:
            save_file = "files/adstore.{}.db".format(self._data["name"])
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
    command = "remove_observer"
    
    def execute(self):
        if "name" not in self._data:
            raise CommandError("The remove_observer command must specify a name.")
        self._server.remove_observer(self._data["name"])


class ListObserversCommand(Command):
    """
    Returns a list of all observers that are currently running.
    """
    command = "list_observers"
    
    def execute(self):
        return [observer.name for observer in self._server]


class GetObserverCommand(Command):
    """
    Returns a list of all observers that are currently running.
    """
    command = "get_observer"
    
    def execute(self):
        if "name" not in self._data:
            raise CommandError("The get_observer command must specify a name.")
        observer = self._server[self._data["name"]]
        if observer is None:
            raise CommandError("Observer {} not found.".format(self._data["name"]))
        return observer.serialize()


class ListCommandsCommand(Command):
    """
    Returns a list of all available commands.
    """
    command = "list_commands"
    
    def execute(self):
        return [cmd_class.command for cmd_class in Command.__subclasses__()]

