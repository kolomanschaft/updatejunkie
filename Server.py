#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Server.py

Created by Martin Hammerschmied on 2013-10-25.
Copyright (c) 2013. All rights reserved.
"""

from Command import command_from_json
import json
import time

class ServerException(Exception):pass

class ServerApp():
    
    def __init__(self, logger):
        self._config = dict()
        self._logger = logger
        self._observers = list()
        
    @property
    def config(self):
        return self._config

    @property
    def observers(self):
        return self._observers

    @property
    def logger(self):
        return self._logger
    
    @logger.setter
    def logger(self, aLogger):
        self._logger = aLogger
    
    def process_json(self, json_string):
        def executeCommand(cmd):
            if ("command" in cmd):
                command = command_from_json(self, cmd)
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