#!/usr/bin/env python3
# encoding: utf-8
"""
main.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
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
    