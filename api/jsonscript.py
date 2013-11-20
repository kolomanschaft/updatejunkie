#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2013 Martin Hammerschmied

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

from api.commandapi import CommandApi

import json
import logging

class JsonScript(CommandApi):
    """
    Processes a command script
    """
    
    def __init__(self, server, path):
        self._path = path
        super(JsonScript, self).__init__(server)
    
    def run(self):
        """
        Takes a path to a command script and processes it. A command script can
        contain a single command dictionary or an array of commands.
        """
        logging.info("Processing command script at {}".format(self._path))
        with open(self._path, "r") as f:
            json_decoded = json.loads(f.read())
            if type(json_decoded) is list:
                for cmd_info in json_decoded: self._process_command_info(cmd_info)
            else:
                self._process_command_info(json_decoded)
        