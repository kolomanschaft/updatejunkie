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

import re

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
        self._valid_key_regex = r"[a-zA-Z0-9_-]+"   # Never include '.' (dot)!! It is used for config paths.
        self._fixed_tree = False
        if tree:
            if type(tree) is not dict:
                raise TypeError("'tree' argument must be a dictionary")
            for key in tree:
                self[key] = tree[key]

    def __setitem__(self, key, value):
        if self._fixed_tree:
            if key not in self:
                raise FixedTreeError("Adding new config node `{}` is not allowed".format(key))
            elif type(self[key]) is ConfigNode:
                if not isinstance(value, dict):
                    raise TypeError("ConfigNode cannot be overwritten by '{}' if tree is fixed".format(type(value)))
                if not self[key]._compare_keys(value):
                    raise FixedTreeError("Keys in tree must be equal if tree is fixed")
        if not re.match(self._valid_key_regex, key):
            raise KeyError("The key '{}' contains illegal characters".format(key))
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

    def _compare_keys(self, other):
        try:
            if set(self.keys()) != set(other.keys()):
                return False
            for key, node in self._get_child_nodes(tuples=True):
                if not node._compare_keys(other[key]):
                    return False
            return True
        except:
            return False

    def _get_child_nodes(self, tuples=False):
        if tuples:
            return [item for item in self.items() if type(item[1]) is ConfigNode]
        else:
            return [self[key] for key in self if type(self[key]) is ConfigNode]

    def __getattr__(self, name):
        """
        Existing keys can be accessed using the attribute notation
        """
        if name in self:
            return self[name]
        else:
            raise AttributeError("No config node {}".format(name))

    def __setattr__(self, key, value):
        """
        Updating existing keys using the attribute syntax is possible. NEW ATTRIBUTES WILL LAND IN `self.__dict__`!!!!
        """
        if key in self.keys():
            self[key] = value
        else:
            super(ConfigNode, self).__setattr__(key, value)

    def update(self, other=None, **kwargs):
        """
        The update method should behave exactly like the built-in dict's update method. Except if the current value is
        a ConfigNode the update value must be a dictionary-like object as well and the current ConfigNode's update
        method should be used instead of a simple assignment. In other words, the whole tree should be updated
        recursively, not only the current ConfigNode.
        """
        if other:
            if hasattr(other, 'keys'):
                for key in other:
                    self._update_key(key, other[key])
            else:
                for key, value in other:
                    self._update_key(key, value)
        for key in kwargs:
            self._update_key(key, kwargs[key])

    def _update_key(self, key, value):
        if key in self and type(self[key]) is ConfigNode:
            self[key].update(value)
        else:
            self[key] = value


    @property
    def fixed_tree(self):
        return self._fixed_tree

    @fixed_tree.setter
    def fixed_tree(self, value):
        """
        If `fixed_tree` is `True` no new keys can be added. Updating the config can only be done with dictionaries that
        do not introduce new keys. Assigning a new value to a ConfigNode will result in an update (instead of
        assignment).
        """
        if type(value) is not bool:
            raise TypeError('`fixed_tree` must be a bool')
        self._fixed_tree = value
        for node in self._get_child_nodes():
            node.fixed_tree = value

class FixedTreeError(Exception): pass