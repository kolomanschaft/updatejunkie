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


def request_handler(handler):
    """
    A decorator for WebApi request handlers. The request handlers only have to convert the request into a command info 
    dictionary and return that. The decorator takes care of the HTTP response and unhandled exceptions.
    """
    def wrapper(*args):
        instance = args[0]
        cmd_info = handler(args)
        try:
            return instance._process_command_info(cmd_info)
        except Exception as error:
            # Relay the error as JSON response
            return {"status": "ERROR", 
                    "message": "{}".format(error.args[0])
                   }
        finally:
            # Make sure the API can be used from every other doman (CORS)
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    return wrapper


class WebApi(CommandApi):
    """
    A RESTful JSON API based on the web framework bottle.py 
    """

    @request_handler
    def _list_observers(self):
        cmd_info = {"command": "list_observers"}
        return cmd_info
            
    def run(self):
        bottle.route("/api/list/observers", "GET")(self._list_observers)
        bottle.run(host="localhost", port="8118", debug=True)