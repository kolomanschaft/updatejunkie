#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2012 Martin Hammerschmied

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

class ProfileBase(object):
    """
    Base class for profiles. The primary purpose of this base class is to 
    provide a starting point for writing your own profiles. All properties and 
    methods in this base class raise a NotImplementedError. Just subclass 
    ProfileBase in a new module within the `profiles` package and implement all 
    of them. Finally give your profile a proper name by overriding the class 
    variable `name`. Thats it. The profiles.get_profile_by_name() function will 
    find your profile automagically.
    """
    
    name = "Unnamed"

    @property
    def tags(self):
        """
        A complete list of tag names that are available for each extracted ad.
        """
        raise NotImplementedError()

    @property
    def key_tag(self):
        """
        The name of the tag that serves as unique identifier.
        """
        raise NotImplementedError()

    @property
    def datetime_tag(self):
        """
        The name of the tag that contains the datetime of an ad.
        """
        raise NotImplementedError()

    @property
    def encoding(self):
        """
        The Websites character encoding.
        """
        raise NotImplementedError()

    def first_page(self, url):
        """
        This is part of the paging mechanism. The paging is expected to be somehow encoded in the URL (e.g. in the
        query string or as part of the relative path). Override this method in a subclass to enable paging.
        :param url: The URL as specified in the observer configuration.
        :return: The URL of the first page.
        """
        return url

    def next_page(self, url):
        """
        This is part of the paging mechanism. It should lead the way from one page to the next. If the return value is
        identical to `url` the connector will assume that there is no more page.
        :param url: Either the return value of first_page() or of a previous call of next_page()
        :return: The URL of the next page (relative to the `url` param)
        """
        return url

    def parse(self, html):
        """
        The magic method that extracts ads from HTML code. This method returns 
        a list of dictionaries where each dictionary represents one ad. Each 
        dictionary contains all tags as specified in the `tags` property.
        """
        raise NotImplementedError()
