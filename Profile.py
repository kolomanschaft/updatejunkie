#!/usr/bin/env python3
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
        if filename[-3:] == "xml":
            p = Profile(folder+filename)
            if p.name == name:
                return p
    raise ProfileError("No connector profile with the name of {} found".format(name))

class Profile(object):
    
    def __init__(self, path):
        if not os.path.exists(path):
            raise ProfileError("File {} does not exist!".format(path))
        dom = parse(path)
        self._profile = self._childNode("profile", dom)
        self._website = self._childNode("website", self._profile)
    
    def _childNodes(self, tag, node = None):
        if not node:
            node = self._website
        return [child for child in node.childNodes if child.nodeName == tag]
    
    def _childNode(self, tag, node = None):
        tags = self._childNodes(tag, node)
        if len(tags) != 1:
            raise ProfileError("Exactly one {} tag allowed! Found {}".format(tag, len(tags)))
        return tags[0]
    
    def _firstTextChild(self, node):
        tags = self._childNodes("#text", node)
        return tags[0]
    
    @property
    def name(self):
        nameNode = self._childNode("name", self._profile)
        return self._firstTextChild(nameNode).nodeValue
    
    @property
    def base_url(self):
        baseUrlNode = self._childNode("baseUrl")
        if not baseUrlNode.hasChildNodes:
            raise ProfileError("Profile baseUrl is empty!")
        return self._firstTextChild(baseUrlNode).nodeValue
    
    @property
    def ad_regex(self):
        adDefinitionNode = self._childNode("adDefinition")
        regexNode = self._childNode("regex", adDefinitionNode)
        if not regexNode.hasChildNodes:
            raise ProfileError("Profile adDefinition lacks a regex!")
        return self._firstTextChild(regexNode).nodeValue
    
    @property
    def ad_tags(self):
        adDefinitionNode = self._childNode("adDefinition")
        tagNodes = self._childNodes("tag", adDefinitionNode)
        tags = [{"name": self._firstTextChild(tagNode).nodeValue, "type": tagNode.getAttribute("type")} for tagNode in tagNodes]
        return tags
    
    @property
    def time_tag(self):
        adDefinitionNode = self._childNode("adDefinition")
        timeTagNode = self._childNode("timeTag", adDefinitionNode)
        tagNameNode = self._childNode("tagName", timeTagNode)
        formatNode = self._childNode("format", timeTagNode)
        return {"name": self._firstTextChild(tagNameNode).nodeValue, "format": self._firstTextChild(formatNode).nodeValue}
    
    @property
    def key_tag(self):
        adDefinitionNode = self._childNode("adDefinition")
        keyTagNode = self._childNode("keyTag", adDefinitionNode)
        tagNameNode = self._childNode("tagName", keyTagNode)
        return self._firstTextChild(tagNameNode).nodeValue
       
    
    @property
    def format_regexes(self):
        def make_dict(regexNode):
            return {"regex": self._firstTextChild(regexNode).nodeValue, "type": regexNode.getAttribute("type")}
        formatNode = self._childNode("format")
        return [make_dict(regexNode) for regexNode in self._childNodes("regex", formatNode)]
    
    @property
    def page_param(self):
        try:
            pageParamNode = self._childNode("pageParam")
        except ProfileError:
            return None
        return {"name": self._firstTextChild(pageParamNode).nodeValue, "method": pageParamNode.getAttribute("method"), "init": int(pageParamNode.getAttribute("init"))} 

    @property
    def notification_email(self):
        try:
            notificationNode = self._childNode("notification", self._profile)
            emailNode = self._childNode("email", notificationNode)
        except ProfileError:
            return None
        emailSubject = self._firstTextChild(self._childNode("subject", emailNode)).nodeValue
        bodyHtml = [node.toxml().strip() for node in self._childNode("body", emailNode).childNodes]
        emailFrom = self._firstTextChild(self._childNode("from", emailNode)).nodeValue
        type = emailNode.getAttribute("type")
        email = {"from": emailFrom, "subject": emailSubject, "body": "\n".join(bodyHtml), "type": type}
        return email

    @property
    def notification_desktop(self):
        try:
            notificationNode = self._childNode("notification", self._profile)
            desktopNode = self._childNode("desktop", notificationNode)
        except ProfileError:
            return None
        title = self._firstTextChild(self._childNode("title", desktopNode)).nodeValue
        body = [node.toxml().strip() for node in self._childNode("body", desktopNode).childNodes]
        try:
            url = self._firstTextChild(self._childNode("url", desktopNode)).nodeValue
        except ProfileError:
            url = None
        return {"title": title, "body": "\n".join(body), "url": url}

if __name__ == '__main__':
    profile = get_profile("Willhaben")
    print("Profile Name:", profile.name)
    print("baseUrl", profile.base_url)
    print("adRegex", profile.ad_regex)
    print("tags", profile.ad_tags)
    print("timeTag", profile.time_tag)
    print("keyTag", profile.key_tag)
    print("format", profile.format_regexes)
    print("pageParam", profile.page_param)
    print("Email notification", profile.notification_email)
    print("Desktop notification", profile.notification_desktop)
    
    