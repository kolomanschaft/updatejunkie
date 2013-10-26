#!/usr/bin/env python3
# encoding: utf-8
"""
main.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""



from Logger import Logger
from Server import ServerApp

import sys
import os
import datetime

if __name__ == "__main__":
 
    dtime = "01.05.2013 23:27"
    dtime_format = "%d.%m.%Y %H:%M"
    datetime.datetime.strptime(dtime, dtime_format)
    
    # Create the 'files/' directory if it doesn't exist yet
    if not os.path.exists("./files/"): os.mkdir("files")
    
    # Configuration script path
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "./files/willhaben.json"
    
    # Initialize logging
    logger = Logger(path = "files/observer.log")

    server = ServerApp(logger)
    
    # If we have a configuration script, process it
    if (os.path.exists(config_path)):
        server.process_command_script(config_path)

    # Run, run, run!
    server.run()
    