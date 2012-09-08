# -*- coding: utf-8 -*-
from AdStore import *
from AdAssessor import *
from WillhabenObserver import *
from Logger import *
import md5
import sys

if __name__ == "__main__":
	
	url = "http://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?ISPRIVATE=1&CATEGORY/SUBCATEGORY=8621&CATEGORY/MAINCATEGORY=73"

	save_file = "files/" + md5.new(url).hexdigest() + ".save"
	store = AdStore(path = save_file)
	
	kwdsAll = AdCriterionTitleKeywordsAll(["galaxy"])
	kwdsAny = AdCriterionTitleKeywordsAny(["s3", "sIII", "i9300"])
	kwdsNot = AdCriterionTitleKeywordsNot(["freischalten"])
	price = AdCriterionPriceLimit(350)
	
	assessor = AdAssessor()
	assessor.add_criteria(kwdsAll, kwdsAny, kwdsNot, price)
	
	logger = Logger(path = "files/observer.log")
	logger.append("Setting up observer")
	
	if sys.platform == "linux2":
		from platform_dependant.Linux import GTKNotification
		notification = GTKNotification(icon = "./logo.png")
		observer = WillhabenObserver(url, store, assessor, notification, update_interval = 60)
		observer.run()
	elif sys.platform == "darwin":
		from threading import Thread
		import Foundation, objc, AppKit
		from PyObjCTools import AppHelper
		from platform_dependant.MacOS import MountainLionNotification
		notification = MountainLionNotification.alloc().init()
		observer = WillhabenObserver(url, store, assessor, notification, logger = logger, update_interval = 60)
		t = Thread(target = observer.run)
		t.start()
		app = AppKit.NSApplication.sharedApplication()
		AppHelper.runEventLoop()