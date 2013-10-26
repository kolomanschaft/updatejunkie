#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command.py

Created by Martin Hammerschmied on 2013-10-25.
Copyright (c) 2013. All rights reserved.
"""

from Profile import get_profile
from AdStore import AdStore
from AdAssessor import *
from NotificationServer import NotificationServer
from Observer import Observer


class CommandError(Exception):pass


class Command(object):

    def __init__(self, server, data):
        self._server = server
        self._data = data
    
    def execute(self):
        raise CommandError("Execute must be implemented in a subclass.")
    
    @classmethod
    def from_json(cls, server, data):
        if ("command" not in data):
            raise CommandError("The given data is not a valid command.")
        
        # Dispatch the command
        if (data["command"] == "new_observer"):
            return NewObserverCommand(server, data)
        elif (data["command"] == "remove_observer"):
            return RemoveObserverCommand(server, data)
        elif (data["command"] == "smtp_config"):
            return SmtpSettingsCommand(server, data)
        
        raise CommandError("Unknown command: {}".format(data["command"]))


class SmtpSettingsCommand(Command):
    
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
    
    def execute(self):
        self._server._logger.append("Setting up observer " + self._data["name"])
        profile = get_profile(self._data["profile"])
        store = self._setup_store()
        assessor = self._setup_assessor()
     
        # Notification server setup
        notificationServer = NotificationServer()
        for json in self._data["notification"]:
            notification = self._setup_notification(json, profile)
            notificationServer.addNotification(notification)

        # Setup the actual observer
        observer = Observer(url = self._data["url"], profile = profile,
                            store = store, assessor = assessor,
                            notification = notificationServer,
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
    
    def _setup_assessor(self):
        assessor = AdAssessor()
        for trigger in self._data["trigger"]:
            if (trigger["type"] == "all"):
                criterion = AdCriterionKeywordsAll(trigger["tag"], trigger["keywords"])
            if (trigger["type"] == "any"):
                criterion = AdCriterionKeywordsAny(trigger["tag"], trigger["keywords"])
            if (trigger["type"] == "not"):
                criterion = AdCriterionKeywordsNot(trigger["tag"], trigger["keywords"])
            if (trigger["type"] == "limit"):
                criterion = AdCriterionLimit(trigger["tag"], trigger["value"])
            assessor.add_criterion(criterion)
        return assessor
            
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
    
    def execute(self):
        if "name" not in self._data:
            raise CommandError("The remove_observer command must specify a name.")
        
        try:
            self._server.remove_observer(self._data["name"])
            return {"status": "OK"}
        except Exception as ex:
            return {"status": "ERROR", "description": "write something"}
        