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

from server import Server
from api.jsonscript import JsonScript
from api.webapi import WebApi

import sys
import os
import datetime
import logging
import signal

if __name__ == "__main__":
 
    dtime = "2013-05-23 23:27"
    dtime_format = "%Y-%m-%d %H:%M"
    datetime.datetime.strptime(dtime, dtime_format)

    # Setup logging
    logging.basicConfig(filename='updatejunkie.log', format='[%(asctime)s] %(message)s', datefmt = dtime_format, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    
    # Create the 'files/' directory if it doesn't exist yet
    if not os.path.exists("./config/"): os.mkdir("config")
    
    # Configuration script path
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "./config/updatejunkie.json"
    
    server = Server()
    server.start()
        
    # If we have a command script, process it
    if (os.path.exists(config_path)):
        config = JsonScript(server, config_path)
        config.run()

    # Start the web API
    server.start_web_api()

    def shutdown(signal, frame):
        logging.info("Caught keyboard interrupt. Shutting down...")
        server.quit()
        server.join()

    # Waiting for Ctrl-c
    signal.signal(signal.SIGINT, shutdown)
    signal.pause()