# -*- coding: utf-8 -*-	
from Notification import *

class GTKNotification(Notification):

	def __init__(self, icon = None):
		import notify2
		if icon:
			from gtk import gdk
			self.icon = gdk.pixbuf_new_from_file(icon)
		else:
			self.icon = None

	def notify(self, title, subtitle, text, url):
		import gobject
		gobject.idle_add(self.show_gtk_notification, (title, subtitle, text, url))
	
	def show_gtk_notification(self, info):
		import notify2, gtk
		notify2.init("Willhaben Observer", "glib")
		notification = notify2.Notification(unicode(info[0]), unicode(info[1]) + "\n" + unicode(info[2]))
		if self.icon:
			notification.set_icon_from_pixbuf(self.icon)
		notification.add_action(info[3], "View ad", self.open_url)
		notification.set_timeout(notify2.EXPIRES_NEVER)
		notification.show()

	def open_url(self, url):
		import webbrowser
		webbrowser.open(url)
