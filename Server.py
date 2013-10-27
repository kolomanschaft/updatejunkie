#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Server.py

Created by Martin Hammerschmied on 2013-10-25.
Copyright (c) 2013. All rights reserved.
"""

from Command import Command, CommandError
from bottle import route, request, response
from bottle import run as bottlerun
import json
import sys

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
        except StopIteration:
            raise ServerError("No observer with the name of {}".format(name))
    
    def __getitem__(self, key):
        if type(key) is not str:
            raise TypeError("The key must be a string containing the observer name.")
        try:
            return next(observer for observer in self._observers if observer.name == key)
        except StopIteration:
            raise KeyError("Observer {} not found".format(key))
    
    def __iter__(self):
        return self._observers.__iter__()
    
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
            try:
                command = Command.from_json(self, cmd)
                response = command.execute()
                response_message = {"status": "OK"}
                if response is not None:
                    response_message["response"] = response
                return response_message
            except (ServerError, CommandError) as ex:
                args_text = "; ".join(["{}".format(arg) for arg in ex.args])
                return {"status": "ERROR", "message": args_text}
        
        if (type(json_data) is dict):
            return executeCommand(json_data)
        elif (type(json_data) is list):
            return [executeCommand(cmd) for cmd in json_data]
        else:
            raise ServerError("Unknown JSON structure.")
    
    def run(self):
        route("/api/command")(self._command)
        bottlerun(host="localhost", port="8118", debug=True)
        
    def _command(self):
        try:
            json_data = request.json
            return self.process_json(json_data)
        except ValueError as error:
            return {"status": "ERROR", 
                    "message": "JSON syntax: {}".format(error.args[0])
                   }
