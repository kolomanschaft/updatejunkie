#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config.py

Created by Martin Hammerschmied on 2012-11-06.
Copyright (c) 2012. All rights reserved.
"""

from xml.dom.minidom import parse
import os
import re

class ProfileError(Exception):pass

class Profile(object):
    
    def __init__(self, path):
        if not os.path.exists(path):
            raise ProfileError("File {} does not exist!".format(path))
        dom = parse(path)
        self._website = self._childNode(u"website", dom)
    
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
    
    def base_url(self):
        baseUrlNode = self._childNode(u"baseUrl")
        if not baseUrlNode.hasChildNodes:
            raise ProfileError("Profile baseUrl is empty!")
        return self._firstTextChild(baseUrlNode).nodeValue
    
    def ad_regex(self):
        adDefinitionNode = self._childNode(u"adDefinition")
        regexNode = self._childNode(u"regex", adDefinitionNode)
        if not regexNode.hasChildNodes:
            raise ProfileError("Profile adDefinition lacks a regex!")
        return self._firstTextChild(regexNode).nodeValue
    
    def ad_tags(self):
        adDefinitionNode = self._childNode(u"adDefinition")
        tagNodes = self._childNodes(u"tag", adDefinitionNode)
        tags = [{"name": self._firstTextChild(tagNode).nodeValue, "type": tagNode.getAttribute(u"type")} for tagNode in tagNodes]
        return tags
    
    def format_regexes(self):
        def make_dict(regexNode):
            return {"regex": self._firstTextChild(regexNode).nodeValue, "type": regexNode.getAttribute(u"type")}
        formatNode = self._childNode(u"format")
        return [make_dict(regexNode) for regexNode in self._childNodes(u"regex", formatNode)]
    
    def page_param(self):
        pageParamNode = self._childNode(u"pageParam")
        return {"name": self._firstTextChild(pageParamNode).nodeValue, "method": pageParamNode.getAttribute(u"method"), "init": int(pageParamNode.getAttribute(u"init"))} 

if __name__ == '__main__':
    path = u"connector_profiles/willhaben.xml"
    profile = Profile(path)
    print "baseUrl", profile.base_url()
    print "adRegex", profile.ad_regex()
    print "tags", profile.ad_tags()
    print "format", profile.format_regexes()
    print "pageParam", profile.page_param()
    