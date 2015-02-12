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

from command import Command
from threading import Thread

class CommandApi(Thread):
    """
    The base for all APIs that process commands. Each API runs in a separate 
    thread. In general APIs translate data they receive on their front-ends 
    into command objects and pass them on to the server. The result is then 
    taken back from the server to the API front-end.
    """

    def __init__(self, server):
        Thread.__init__(self)
        self._server = server
        self.name = "CommandApi"

    def _process_command_info(self, cmd_info):
        command = Command.from_command_info(cmd_info)
        command.condition.acquire()
        self._server.enqueue_command(command)
        command.condition.wait()
        command.condition.release()
        return command.response
