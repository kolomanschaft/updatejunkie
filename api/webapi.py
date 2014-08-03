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

import imp
bottle = imp.load_source('bottle', 'api/bottle/bottle.py')

from api.commandapi import CommandApi

class WebApi(CommandApi):
    """
    A RESTful JSON API based on the web framework bottle.py 
    """
        
    def _command(self):
        try:
            json_decoded = bottle.request.json
            return self._process_command_info(json_decoded)
        except Exception as error:
            # Relay the error as JSON response
            return {"status": "ERROR", 
                    "message": "{}".format(error.args[0])
                   }
            
    def run(self):
        bottle.route("/api/command")(self._command)
        bottle.run(host="localhost", port="8118", debug=True)