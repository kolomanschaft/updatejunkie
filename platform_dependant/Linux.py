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
		import notify2, gtk
		notify2.init("Willhaben Observer", "glib")
		notification = notify2.Notification(unicode(title), unicode(subtitle) + "\n" + unicode(text))
		if self.icon:
			notification.set_icon_from_pixbuf(self.icon)
		notification.add_action(url, "View ad", open_url)
		#notification.set_timeout(notify2.EXPIRES_NEVER)
		notification.show()
		gtk.main()


def open_url(self, url):
	import webbrowser
	webbrowser.open_new_tab(url)
