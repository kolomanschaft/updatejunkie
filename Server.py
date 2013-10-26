#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Server.py

Created by Martin Hammerschmied on 2013-10-25.
Copyright (c) 2013. All rights reserved.
"""

from Command import Command
from bottle import route, request
from bottle import run as bottlerun
import json

class ServerError(Exception):pass

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
    
    def process_command_script(self, path):
        with open(path, "r") as f:
            json_data = json.loads(f.read())
            self.process_json(json_data)
        
    def process_json(self, json_data):
        def executeCommand(cmd):
            command = Command.from_json(self, cmd)
            command.execute()
        if (type(json_data) is dict):
            executeCommand(json_data)
        elif (type(json_data) is list):
            for cmd in json_data: executeCommand(cmd)
        else:
            raise ServerError("Unknown JSON structure.")
    
    def run(self):
        route("/api/command")(self._command)
        bottlerun(host="localhost", port="8118", debug=True)
        
    def _command(self):
        if request.json:
            self.process_json(request.json)
