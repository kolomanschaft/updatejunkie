#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Server.py

Created by Martin Hammerschmied on 2013-10-25.
Copyright (c) 2013. All rights reserved.
"""

from Command import Command
import json
import time

class ServerException(Exception):pass

class ServerApp():
    
    def __init__(self, logger):
        self._config = dict()
        self._logger = logger
        self._observers = list()

    def add_observer(self, observer):
        if (observer.name in [other.name for other in self._observers]):
            self._logger.append("Replacing observer {}".format(observer.name))
            self.remove_observer(observer.name)
            
        self._observers.append(observer)
        observer.start()
    
    def remove_observer(self, name):
        try:
            observer = next(observer for observer in self._observers if observer.name == name)
            observer.quit()
            self._observers.remove(observer)
        except StopIteration:pass
        
    @property
    def config(self):
        return self._config

    @property
    def logger(self):
        return self._logger
    
    @logger.setter
    def logger(self, aLogger):
        self._logger = aLogger
    
    def process_json(self, json_string):
        def executeCommand(cmd):
            if ("command" in cmd):
                command = Command.from_json(self, cmd)
                command.execute()
                
        data = json.loads(json_string)
        if (type(data) is dict):
            executeCommand(data)
        elif (type(data) is list):
            for cmd in data: executeCommand(cmd)
        else:
            raise ServerException("Unknown json structure.")

    def run(self):
        while True:
            time.sleep(1)