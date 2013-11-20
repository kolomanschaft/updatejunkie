#!/usr/bin/env python3
# encoding: utf-8
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

from logger import Logger
from server import ServerApp

import sys
import os
import datetime

if __name__ == "__main__":
 
    dtime = "01.05.2013 23:27"
    dtime_format = "%d.%m.%Y %H:%M"
    datetime.datetime.strptime(dtime, dtime_format)
    
    # Create the 'files/' directory if it doesn't exist yet
    if not os.path.exists("./config/"): os.mkdir("config")
    
    # Configuration script path
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "./config/updatejunkie.json"
    
    # Initialize logging
    logger = Logger(path = "updatejunkie.log")

    server = ServerApp(logger)
    
    # If we have a command script, process it
    if (os.path.exists(config_path)):
        server.process_command_script(config_path)

    # Run, run, run!
    server.run()
    