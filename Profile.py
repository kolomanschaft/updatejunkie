#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config.py

Created by Martin Hammerschmied on 2012-11-06.
Copyright (c) 2012. All rights reserved.
"""

from xml.dom.minidom import parse
import os

class ProfileError(Exception):pass

def get_profile(name):
    folder = "connector_profiles/"
    filenames = os.listdir(folder)
    for filename in filenames:
        if filename[-3:] == u"xml":
            p = Profile(folder+filename)
            if p.name == name:
                return p
    raise ProfileError("No connector profile with the name of {} found".format(name))

class Profile(object):
    
    def __init__(self, path):
        if not os.path.exists(path):
            raise ProfileError("File {} does not exist!".format(path))
        dom = parse(path)
        self._profile = self._childNode(u"profile", dom)
        self._website = self._childNode(u"website", self._profile)
    
    def _childNodes(self, tag, node = None):
        if not node:
            node = self._website
        return filter(lambda child: child.nodeName == tag, node.childNodes)
    
    def _childNode(self, tag, node = None):
        tags = self._childNodes(tag, node)
        if len(tags) != 1:
            raise ProfileError("Exactly one {} tag allowed! Found {}".format(tag, len(tags)))
        return tags[0]
    
    def _firstTextChild(self, node):
        tags = self._childNodes(u"#text", node)
        return tags[0]
    
    @property
    def name(self):
        nameNode = self._childNode(u"name", self._profile)
        return self._firstTextChild(nameNode).nodeValue
    
    @property
    def base_url(self):
        baseUrlNode = self._childNode(u"baseUrl")
        if not baseUrlNode.hasChildNodes:
            raise ProfileError("Profile baseUrl is empty!")
        return self._firstTextChild(baseUrlNode).nodeValue
    
    @property
    def ad_regex(self):
        adDefinitionNode = self._childNode(u"adDefinition")
        regexNode = self._childNode(u"regex", adDefinitionNode)
        if not regexNode.hasChildNodes:
            raise ProfileError("Profile adDefinition lacks a regex!")
        return self._firstTextChild(regexNode).nodeValue
    
    @property
    def ad_tags(self):
        adDefinitionNode = self._childNode(u"adDefinition")
        tagNodes = self._childNodes(u"tag", adDefinitionNode)
        tags = [{"name": self._firstTextChild(tagNode).nodeValue, "type": tagNode.getAttribute(u"type")} for tagNode in tagNodes]
        return tags
    
    @property
    def time_tag(self):
        adDefinitionNode = self._childNode(u"adDefinition")
        timeTagNode = self._childNode(u"timeTag", adDefinitionNode)
        tagNameNode = self._childNode(u"tagName", timeTagNode)
        formatNode = self._childNode(u"format", timeTagNode)
        return {"name": self._firstTextChild(tagNameNode).nodeValue, "format": self._firstTextChild(formatNode).nodeValue}
    
    @property
    def key_tag(self):
        adDefinitionNode = self._childNode(u"adDefinition")
        keyTagNode = self._childNode(u"keyTag", adDefinitionNode)
        tagNameNode = self._childNode(u"tagName", keyTagNode)
        return self._firstTextChild(tagNameNode).nodeValue
       
    
    @property
    def format_regexes(self):
        def make_dict(regexNode):
            return {"regex": self._firstTextChild(regexNode).nodeValue, "type": regexNode.getAttribute(u"type")}
        formatNode = self._childNode(u"format")
        return [make_dict(regexNode) for regexNode in self._childNodes(u"regex", formatNode)]
    
    @property
    def page_param(self):
        pageParamNode = self._childNode(u"pageParam")
        return {"name": self._firstTextChild(pageParamNode).nodeValue, "method": pageParamNode.getAttribute(u"method"), "init": int(pageParamNode.getAttribute(u"init"))} 

if __name__ == '__main__':
    profile = get_profile(u"willhaben")
    print "Profile Name:", profile.name()
    print "baseUrl", profile.base_url()
    print "adRegex", profile.ad_regex()
    print "tags", profile.ad_tags()
    print "timeTag", profile.time_tag()
    print "keyTag", profile.key_tag()
    print "format", profile.format_regexes()
    print "pageParam", profile.page_param()
    