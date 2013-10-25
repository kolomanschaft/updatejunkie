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

def command_from_json(server, data):
    if ("command" not in data):
        raise CommandException("The given data is not a valid command.")
    
    if (data["command"] == "settings"):
        return SettingsCommand(server, data)
    elif (data["command"] == "observer"):
        return ObserverCommand(server, data)


class CommandException(Exception):pass


class Command(object):

    def __init__(self, server, data):
        self._server = server
        self._data = data
    
    def execute(self):
        raise CommandException("Execute must be implemented in a subclass.")


class SettingsCommand(Command):
    
    def execute(self):
        if ("smtp" in self._data):
            self.validate_smtp(self._data["smtp"])
            self._server.config["smtp"] = self._data["smtp"]
    
    def validate_smtp(self, config):
        if ("host" not in config):
            raise CommandException("'host' is missing in the smtp configuration.")
        if ("port" not in config):
            raise CommandException("'port' is missing in the smtp configuration.")


class ObserverCommand(Command):
    
    def execute(self):
        self._server._logger.append("Setting up observer " + self._data["name"])
        profile = get_profile(self._data["profile"])
        
        # Ads that have already been processed are registered in this file
        save_file = None
        if self._data["store"] == True:
            save_file = "files/adstore.{}.db".format(self._data["name"])
        else: 
            save_file = None    
        store = AdStore(path = save_file)
     
        # Search criteria setup
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
     
        # Notification server setup
        notificationServer = NotificationServer()
        for notification in self._data["notification"]:
            if (notification["type"] == "email"):
                if not self._server.config["smtp"]:
                    raise CommandException("Cannot setup email notifications without smtp settings.")

                from platform_dependant.Notification import EmailNotification
                formatting = profile.Notifications.Email

                smtp = self._server.config["smtp"]
                to = notification["to"]
                if (type(to) == str):
                    to = [to]   # make it a list
                
                emailNotify = EmailNotification(smtp["host"],
                                                smtp["port"],
                                                smtp["user"],
                                                smtp["pass"],
                                                formatting.From,
                                                notification["to"],
                                                formatting.ContentType,
                                                formatting.Subject,
                                                formatting.Body.valueOf_)
                notificationServer.addNotification(emailNotify)
 
        observer = Observer(url = self._data["url"],
                            profile = profile,
                            store = store,
                            assessor = assessor,
                            notification = notificationServer,
                            logger = self._server.logger,
                            update_interval = self._data["interval"],
                            name = self._data["name"])
        
        self._server.observers.append(observer)
        observer.start()
