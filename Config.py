#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import ConfigParser
import os
import re

class ConfigError(Exception): pass


class WillhabenConfigParser(ConfigParser.SafeConfigParser, object):
    
    def _probe_section(self, section):
        if not self.has_section(section):
            self.add_section(section)
    
    def set(self, section, option, value):
        self._probe_section(section)
        super(WillhabenConfigParser, self).set(section, option, value)
    
    def get(self, section, option):
        s = super(WillhabenConfigParser, self).get(section, option)
        if type(s) == unicode:
            return s
        return unicode(s, "utf-8")
    
    def setint(self, section, option, anint):
        if not type(anint) is int:
            raise TypeError("Section {} option {} must be an integer number".format(section, option))
        self.set(section, option, str(anint))
    
    def getlist(self, section, option, rtype = unicode):
        v = [rtype(s.strip()) for s in self.get(section, option).split(",")]
        return v
    
    def setlist(self, section, option, alist):
        if not type(alist) is list:
            raise TypeError("Section {} option {} must be a list".format(section, option))
        self.set(section, option, ", ".join(alist))

    def setboolean(self, section, option, abool):
        if not type(abool) is bool:
            raise TypeError("Section {} option {} must be a bool".format(section, option))
        if abool: self.set(section, option, "yes")
        else: self.set(section, option, "no")

    def options_fitting(self, section, pattern):
        items = [item[0] for item in self.items(section)]
        fitting = filter(lambda item: re.match(pattern, item), items)
        return fitting

    def wildcard_options(self, section, pattern, getter = None):
        if not getter: getter = self.getlist
        options = self.options_fitting(section, pattern)
        all_options = []
        for option in options:
            wildcard = re.match(pattern, option).groups()[0]
            value = getter(section, option)
            all_options.append({"wildcard": wildcard, "value": value})
        return all_options

class ObserverConfig(object):
    
    def __init__(self, parser, name):
        self._parser = parser
        self._name = name
        if not self._parser.has_section(name):
            # This observer seems to be new
            self._setup()
    
    def _setup(self):
        if self._parser.has_section("Observers"):
            observers = self._parser.getlist("Observers", "observers")
            if not self._name in observers:
                observers.append(self._name)
                self._parser.setlist("Observers", "observers", observers)
        else:
            self._parser.add_section("Observers")
            self._parser.set("Observers", "observers", self._name)
        self._parser.add_section(self._name)
        self.url = "http://example.com/"
        self.ads_store = True
        self.update_interval = 120
        self.price_limit = 0
        self.email_to = ["John Doe <john.doe@example.com>"]
        self.notification_title = "{title}"
        self.notification_body = "{title}"
        self.osx_active = False
        self.gtk_active = False
        self.email_active = True

    @property
    def profile(self):
        return self._parser.get(self._name, "profile")
    
    @profile.setter
    def profile(self, aprofile):
        self._parser.set(self._name, "profile", aprofile)
    
    @property
    def url(self):
        return self._parser.get(self._name, "url")
    
    @url.setter
    def url(self, url):
        self._parser.set(self._name, "url", url)

    @property
    def ads_store(self):
        return self._parser.getboolean(self._name, "ads.store")
    
    @ads_store.setter
    def ads_store(self, value):
        self._parser.setboolean(self._name, "ads.store", value)

    @property
    def update_interval(self):
        return self._parser.getint(self._name, "update.interval")

    @update_interval.setter
    def update_interval(self, interval):
        self._parser.setint(self._name, "update.interval", interval)
    
    @property
    def keywords_all(self):
        pattern = r"keywords\.(.+)\.all"
        return self._parser.wildcard_options(self._name, pattern)

    @keywords_all.setter
    def keywords_all(self, options):
        for option in options:
            option_name = "keywords.{}.all".format(option["wildcard"])
            self._parser.setlist(self._name, option_name, option["value"])

    @property
    def keywords_any(self):
        pattern = r"keywords\.(.+)\.any"
        return self._parser.wildcard_options(self._name, pattern)

    @keywords_any.setter
    def keywords_any(self, options):
        for option in options:
            option_name = "keywords.{}.any".format(option["wildcard"])
            self._parser.setlist(self._name, option_name, option["value"])

    @property
    def keywords_not(self):
        pattern = r"keywords\.(.+)\.not"
        return self._parser.wildcard_options(self._name, pattern)

    @keywords_not.setter
    def keywords_not(self, options):
        for option in options:
            option_name = "keywords.{}.not".format(option["wildcard"])
            self._parser.setlist(self._name, option_name, option["value"])

    @property
    def limits(self):
        pattern = r"limit\.(.+)"
        return self._parser.wildcard_options(self._name, pattern, self._parser.getint)

    @limits.setter
    def limits(self, options):
        for option in options:
            option_name = "limit.{}".format(option["wildcard"])
            self._parser.setint(self._name, option_name, option["value"])

    @property
    def email_to(self):
        return self._parser.getlist(self._name, "email.to")

    @email_to.setter
    def email_to(self, to):
        self._parser.setlist(self._name, "email.to", to)

    @property
    def osx_active(self):
        return self._parser.getboolean(self._name, "osx.active")

    @osx_active.setter
    def osx_active(self, active):
        self._parser.setboolean(self._name, "osx.active", active)

    @property
    def gtk_active(self):
        return self._parser.getboolean(self._name, "gtk.active")

    @gtk_active.setter
    def gtk_active(self, active):
        self._parser.setboolean(self._name, "gtk.active", active)

    @property
    def email_active(self):
        return self._parser.getboolean(self._name, "email.active")

    @email_active.setter
    def email_active(self, active):
        self._parser.setboolean(self._name, "email.active", active)


class Config(object):
    
    def __init__(self, path):
        self.path = path
        self._parser = WillhabenConfigParser()
        self.load()

    def save(self):
        with open(self.path, "w") as cfg:
            self._parser.write(cfg)
    
    def load(self):
        if os.path.exists(self.path):
            self._parser.read(self.path)
        else:
            # This config seems to be new. Setting some defaults.
            self.smtp_host = "smtp.example.com"
            self.smtp_port = 25
            self.smtp_user = "user553"
            self.smtp_password = "secret678"
            self.email_from = "Willhaben <contact@willhaben.at>"
        for observer in self.list_observers():
            if not self._parser.has_section(observer):
                raise ConfigError("Observer section {} not found!".format(observer))
            self.add_observer(observer)
        self._sanity_check()

    def _sanity_check(self):
        osx = False
        gtk = False
        for observer in self.list_observers():
            oconfig = self.observer_config(observer)
            if oconfig.osx_active:
                osx = True
            if oconfig.gtk_active:
                gtk = True
        if osx and gtk:
            raise ConfigError("OSX notifications and GTK notifications cannot be active at the same time!")

    @property
    def smtp_host(self):
        return self._parser.get("General", "smtp.host")

    @smtp_host.setter
    def smtp_host(self, host):
        self._parser.set("General", "smtp.host", host)

    @property
    def smtp_port(self):
        return self._parser.getint("General", "smtp.port")

    @smtp_port.setter
    def smtp_port(self, port):
        self._parser.setint("General", "smtp.port", port)

    @property
    def smtp_user(self):
        return self._parser.get("General", "smtp.user")

    @smtp_user.setter
    def smtp_user(self, user):
        self._parser.set("General", "smtp.user", user)

    @property
    def smtp_password(self):
        return self._parser.get("General", "smtp.password")

    @smtp_password.setter
    def smtp_password(self, pw):
        self._parser.set("General", "smtp.password", pw)

    @property
    def email_from(self):
        return self._parser.get("General", "email.from")

    @email_from.setter
    def email_from(self, sender):
        self._parser.set("General", "email.from", sender)

    def list_observers(self):
        try:
            return self._parser.getlist("Observers", "observers")
        except ConfigParser.NoSectionError:
            return []
    
    def observer_config(self, name):
        return getattr(self, name)
    
    def add_observer(self, name):
        setattr(self, name, ObserverConfig(self._parser, name))


if __name__ == '__main__':
    
    # create test config
    
    path1 = "./files/willhaben.cfg"
    c = Config(path1)
    oc = c.observer_config(u"Galaxy")
    print oc.limits
    print oc.keywords_all
    print oc.keywords_any