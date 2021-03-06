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

from api.bottle import bottle
from threading import Thread, Condition
import urllib.request

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
        try:
            cmd_info = handler(*args, **kwargs)
            if bottle.request.method == "OPTIONS":  # OPTIONS requests are used for AJAX preflight requests only.
                return
            response = instance._process_command_info(cmd_info)
            if response["status"] == "ERROR":
                bottle.response.status = 400
                return "Error: {}".format(response["message"])
            else:
                return response["response"]
        except Exception as error:
            # Relay the error as a 500 errror and a JSON message
            bottle.response.status = 500
            return "Uncaught exception: {}".format(error.args[0])
        finally:
            # Make sure the API can be used from every other domain (CORS)
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    return wrapper


class WebApi(CommandApi):
    """
    A RESTful JSON API based on the web micro framework bottle.py
    """

    def __init__(self, server, host="localhost", port=8118):
        CommandApi.__init__(self, server)
        self.name = "WebApi"
        self._host = host
        self._port = port
        self._bottle = None
        self._client_path = None
        self._ready = False
        self._ready_cv = Condition()
        self._register_routes()

    @api_call
    def _list_observers(self):
        return {"command": "list_observers"}

    @api_call
    def _get_observer(self, name):
        return {"command": "get_observer", "name": name}

    @api_call
    def _set_config(self, pathname=None):
        try:
            path_fragments = reversed(pathname.split('/'))
        except AttributeError:
            path_fragments = []
        config = bottle.request.json
        for fragment in path_fragments: # include path as dict-tree
            config = {fragment: config}
        cmd = dict(command="set_config", config=config)
        return cmd

    @api_call
    def _get_config(self, pathname=None):
        try:
            config_path = pathname.replace('/', '.')
        except AttributeError:
            config_path = ""
        cmd = dict(command="get_config", path=config_path)
        return cmd

    @api_call
    def _create_observer(self, name):
        cmd = bottle.request.json
        cmd["command"] = "create_observer"
        cmd["name"] = name
        return cmd

    @api_call
    def _remove_observer(self, name):
        return {"command": "remove_observer", "name": name}

    @api_call
    def _add_notification(self, name):
        cmd = bottle.request.json
        cmd["command"] = "add_notification"
        cmd["observer"] = name
        return cmd

    @api_call
    def _pause_observer(self, name):
        return {"command": "pause_observer", "name": name}

    @api_call
    def _resume_observer(self, name):
        return {"command": "resume_observer", "name": name}

    @api_call
    def _list_commands(self):
        return {"command": "list_commands"}

    @api_call
    def _observer_state(self, name):
        return {"command": "observer_state", "name": name}

    def _register_routes(self):
        self._bottle = bottle.Bottle()
        self._bottle.route("/api/list/observers", "GET")(self._list_observers)
        self._bottle.route("/api/list/commands", "GET")(self._list_commands)
        self._bottle.route("/api/observer/<name>", "GET")(self._get_observer)
        self._bottle.route("/api/observer/<name>", ["PUT", "OPTIONS"])(self._create_observer)
        self._bottle.route("/api/observer/<name>", "DELETE")(self._remove_observer)
        self._bottle.route("/api/observer/<name>/pause", ["PUT", "OPTIONS"])(self._pause_observer)
        self._bottle.route("/api/observer/<name>/resume", ["PUT", "OPTIONS"])(self._resume_observer)
        self._bottle.route("/api/observer/<name>/state", "GET")(self._observer_state)
        self._bottle.route("/api/observer/<name>/notification", ["POST", "OPTIONS"])(self._add_notification)
        self._bottle.route("/api/config", ["GET", "OPTIONS"])(self._get_config)
        self._bottle.route("/api/config/<pathname:path>", ["GET", "OPTIONS"])(self._get_config)
        self._bottle.route("/api/config", "PUT")(self._set_config)
        self._bottle.route("/api/config/<pathname:path>", "PUT")(self._set_config)

        def alive_helper():
            bottle.response.status = 200
        self._bottle.route("/api/alive", "GET")(alive_helper)

    def run(self):
        # Thread sets the self._ready flag True when the API is alive
        self._ready_thread = Thread(target=self._block_test_ready, name="WebApiTestReady", daemon=True)
        self._ready_thread.start()

        self._bottle_server = bottle.WSGIRefServer(host=self._host, port=self._port)
        self._bottle.run(server=self._bottle_server, debug=True, quiet=True)
        self._bottle_server.srv.socket.close()  # Prevents unclosed socket warning

    @property
    def bottle(self):
        return self._bottle

    def wait_ready(self):
        """
        Blocks until the API is up and ready to process commands.
        """
        if self._ready:
            return
        self._ready_cv.acquire()
        self._ready_cv.wait()
        self._ready_cv.release()

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

    def _block_test_ready(self):
        import time
        while(True):
            if self.ready():
                self._ready = True
                self._ready_cv.acquire()
                self._ready_cv.notify_all()
                self._ready_cv.release()
                return
            time.sleep(0.05)

    def register_static_directory(self, static_root, rel_url, default_file=None):
        """
        The API's web server can be used to deliver static content such as a web client. This method must be called
        *after* start() was called.
        :param static_root: Path to the static content (must be a folder)
        :param rel_url: Relative URL to the static content (e.g. "/client")
        :param default_file: Served when the root URL is requested (e.g. "index.html")
        """
        def get_static_file(filepath):
            return bottle.static_file(filepath, static_root)
        self._bottle.route("{}/<filepath:path>".format(rel_url))(get_static_file)
        if default_file:
            def get_default_file():
                return bottle.static_file(default_file, static_root)
            self._bottle.route("{}/".format(rel_url))(get_default_file)

    def quit(self):
        if self.ready():
            self._bottle_server.srv.shutdown()