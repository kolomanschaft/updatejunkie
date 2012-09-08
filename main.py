# -*- coding: utf-8 -*-
from AdStore import *
from AdAssessor import *
from WillhabenObserver import *
from Logger import *
import md5
import sys
import os

if __name__ == "__main__":
	
	# Ads will be observed from this URL
	url = "http://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?ISPRIVATE=1&CATEGORY/SUBCATEGORY=8621&CATEGORY/MAINCATEGORY=73"
	
	# Create the 'files/' directory if it doesn't exist yet
	if not os.path.exists("./files/"): os.mkdir("files")
	
	# Initialize logging
	logger = Logger(path = "files/observer.log")
	logger.append("Setting up observer")
	
	# ----------------------------------------------
	# Set up of the platform independent components
	# ----------------------------------------------
	
	# Ads that have already been processed are registered in this file
	save_file = "files/" + md5.new(url).hexdigest() + ".save"	
	store = AdStore(path = save_file)
	
	# Set up your search criteria here!
	kwdsAll = AdCriterionTitleKeywordsAll(["galaxy"])
	kwdsAny = AdCriterionTitleKeywordsAny(["s3", "sIII", "i9300"])
	kwdsNot = AdCriterionTitleKeywordsNot(["freischalten"])
	price = AdCriterionPriceLimit(400)
	
	assessor = AdAssessor()
	assessor.add_criteria(kwdsAll, kwdsAny, kwdsNot, price)
	
	observer = WillhabenObserver(url, store, assessor, logger = logger, update_interval = 60)
	
	# ---------------------------------------------------------------
	# Set up of the platform dependent components and run event loop
	# ---------------------------------------------------------------
	
	if sys.platform == "linux2":
		from platform_dependant.Linux import GTKNotification
		import gtk, gobject
		GTKNotify = GTKNotification(icon = "./logo.png")
		observer.notification = GTKNotify
		print "Starting observer thread now"
		observer.start()
		gobject.threads_init()
		gtk.main()

	elif sys.platform == "darwin":
		import Foundation, objc, AppKit
		from PyObjCTools import AppHelper
		from platform_dependant.MacOS import MountainLionNotification
		MLNotify = MountainLionNotification.alloc().init()
		observer.notification = MLNotify
		t = Thread(target = observer.run)
		t.start()
		app = AppKit.NSApplication.sharedApplication()
		AppHelper.runEventLoop()
