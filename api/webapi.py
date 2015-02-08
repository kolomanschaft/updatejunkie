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
import urllib.request
bottle = imp.load_source('bottle', 'api/bottle/bottle.py')

from api.commandapi import CommandApi

class WebApiError(Exception):
    pass

def api_call(handler):
    """
    A decorator for WebApi call handlers. The handlers only have to convert the request into a command info
    dictionary and return that. The decorator takes care of the HTTP response and unhandled exceptions.
    """
    def wrapper(*args, **kwargs):
        instance = args[0]
        cmd_info = handler(*args, **kwargs)
        try:
            response = instance._process_command_info(cmd_info)
            if response["status"] == "ERROR":
                bottle.response.status = 500
            return response
        except Exception as error:
            # Relay the error as a 500 errror and a JSON message
            bottle.response.status = 500
            return { "status": "ERROR",
                     "message": "{}".format(error.args[0])
            } # TODO: Exposing internals like this might be a bad idea
        finally:
            # Make sure the API can be used from every other domain (CORS)
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    return wrapper


class WebApi(CommandApi):
    """
    A RESTful JSON API based on the web framework bottle.py 
    """

    def __init__(self, server, host="localhost", port=8118):
        CommandApi.__init__(self, server)
        self.name = "WebApi"
        self._host = host
        self._port = port

    @api_call
    def _list_observers(self):
        return {"command": "list_observers"}

    @api_call
    def _get_observer(self, name):
        return {"command": "get_observer", "name": name}

    def ready(self):
        """
        Check whether the API is ready to process commands
        """
        try:
            self._bottle_server.srv
        except AttributeError:
            return False    # No server, we can stop right here
        url = "http://{}:{}/api/alive".format(self._host, self._port)
        try:
            urllib.request.urlopen(url)
        except:
            return False    # Request failed for some reason
        else:
            return True

    def _alive(self):
        bottle.response.status = 200

    def quit(self):
        if self.ready():
            self._bottle_server.srv.shutdown()

    def run(self):
        bottle.route("/api/list/observers", "GET")(self._list_observers)
        bottle.route("/api/observer/<name>", "GET")(self._get_observer)
        bottle.route("/api/alive", "GET")(self._alive)
        self._bottle_server = bottle.WSGIRefServer(host=self._host, port=self._port)
        bottle.run(server=self._bottle_server, debug=True, quiet=True)