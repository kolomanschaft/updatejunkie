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

import sys
import os
import logging
import signal
import argparse

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--launch-script", type=str, default="./config/updatejunkie.json",
                        help="Specify a command script that will be executed at launch")
    verbosity = dict(DEBUG=logging.DEBUG, INFO=logging.INFO, SILENT=100)
    parser.add_argument("-v", "--verbosity", type=str, choices=verbosity.keys(), default="INFO",
                        help="Set verbosity (Default is INFO)")
    args = parser.parse_args()

    # Setup logging
    dtime_format = "%Y-%m-%d %H:%M"
    logging.basicConfig(filename='updatejunkie.log', format='[%(asctime)s] %(message)s', datefmt = dtime_format,
                        level=verbosity[args.verbosity])
    logging.getLogger().addHandler(logging.StreamHandler())

    # Start the engines!
    server = Server()
    server.daemon = True
    server.start()
        
    # Process the launch script
    try:
        config = JsonScript(server, args.launch_script)
        config.run()
    except FileNotFoundError:
        logging.error("Command script not found: {}".format(args.launch_script))

    # Start the web API
    server.start_web_api()

    # Register web client
    client_root = "{}/client/".format(os.path.dirname(os.path.abspath(__file__)))
    server.register_client(client_root)

    def shutdown(signal, frame):
        logging.info("Caught keyboard interrupt. Shutting down...")
        server.quit()
        server.join(timeout=10)
        if server.is_alive():
            logging.warning("Timeout while waiting for the server to shut down. Force exiting now.")

    # Waiting for Ctrl-c
    signal.signal(signal.SIGINT, shutdown)
    signal.pause()
