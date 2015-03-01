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

def Config(tree, fixed=False):
    """
    Create a tree-structured configuration from a dictionary. The tree can be queried using attribute notation.
    :param tree: A dictionary who's values can either be more dictionaries or a primitive value type.
    :param fixed: If `True` the configuration tree is fixed. No further nodes can be added to the config.
    :return: The root ConfigNode object.
    """
    config = ConfigNode(tree)
    config.fixed_tree = fixed
    return config

class ConfigNode(dict):
    """
    A specialized dictionary that acts as a node in a tree-like data structure used to store configuration information.
    Each node can have an arbitrary number of children. Each child can either be another ConfigNode or one out of
    several primitive value types (see self._value_types).
    """

    def __init__(self, tree=None):
        self._parent = None
        self._value_types = [int, float, bool, str, type(None)]
        self._fixed_tree = False
        if tree:
            if type(tree) is not dict:
                raise TypeError("'tree' argument must be a dictionary")
            for key in tree:
                self[key] = tree[key]

    def __setitem__(self, key, value):
        if key not in self and self._fixed_tree:
            raise FixedTreeError("Adding new config nodes is not allowed")
        if type(value) == ConfigNode:
            value._parent = self
            super(ConfigNode, self).__setitem__(key, value)
        elif type(value) == dict:
            node = ConfigNode(value)
            node._parent = self
            super(ConfigNode, self).__setitem__(key, node)
        elif type(value) in self._value_types:
            super(ConfigNode, self).__setitem__(key, value)
        else:
            raise TypeError("Did not expect value type '{}'".format(type(value)))

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No config node {}".format(name))

    @property
    def fixed_tree(self):
        return self._fixed_tree

    @fixed_tree.setter
    def fixed_tree(self, value):
        if type(value) is not bool:
            raise TypeError('`fixed_tree` must be a bool')
        self._fixed_tree = value

class FixedTreeError(Exception): pass