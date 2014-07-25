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
    def datetime_tag_format(self):
        """
        Format information for the datetime string following the specifications 
        of strptime().
        """
        raise NotImplementedError()

    @property
    def paging_param(self):
        """
        If the profile supports paging (each page is limited to a certain
        number of ads) this is the name of the HTTP parameter that specifies
        the page. (The only supported paging parameter type is integer)
        """
        raise NotImplementedError()

    @property
    def paging_param_init(self):
        """
        The initial value of the paging parameter. Typically 0 or 1.
        """
        raise NotImplementedError()

    @property
    def paging_method(self):
        """
        The method for the paging parameter. This property is usually "GET".
        """
        raise NotImplementedError()

    @property
    def encoding(self):
        """
        The Websites character encoding.
        """
        raise NotImplementedError()

    def parse(self, html):
        """
        The magic method that extracts ads from HTML code. This method returns 
        a list of dictionaries where each dictionary represents one ad. Each 
        dictionary contains all tags as specified in the `tags` property.
        """
        raise NotImplementedError()
