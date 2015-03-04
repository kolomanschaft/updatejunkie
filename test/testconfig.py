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

import unittest
from config import *

class TestConfigNode(unittest.TestCase):

    def setUp(self):
        self._template = {
            'a': 1,
            'b': {
                'c': 'test',
                'd': {
                    'f': 'value'
                }
            }
        }

    def test_config_from_dict(self):
        config = Config(self._template)
        self.assertDictEqual(self._template, config)
        config['x'] = {'new': 'dict'}
        self.assertIs(type(config['x']), ConfigNode)

    def test_illegal_value_type(self):
        class bla: pass
        self._template['x'] = bla()
        def convert():
            Config(self._template)
        self.assertRaises(TypeError, convert)

    def test_config_attribute_access(self):
        config = Config(self._template)
        self.assertEqual('value', config.b.d.f)
        config.b.d.f = 25
        self.assertEqual(25, config.b.d['f'])

    def test_fixed_tree_simple(self):
        config = Config({})
        config['anode'] = 5
        self.assertEqual(config.anode, 5)
        def fix_and_add():
            config.fixed_tree = True
            config['anothernode'] = 3
        self.assertRaises(FixedTreeError, fix_and_add)

    def test_fixed_tree_node_assignment(self):
        config = Config(self._template, fixed=True)
        def assign_wrong_type():
            config.b = 25
        self.assertRaises(TypeError, assign_wrong_type)
        config.b = dict(c=5, d=dict(f=10))  # This should work
        def assign_illegal_node():
            config.b = dict(c=5, d=dict())  # Is missing the 'f' key
        self.assertRaises(FixedTreeError, assign_illegal_node)

    def test_update(self):
        config = Config(self._template)
        # update with dict
        config.update({'g': {}})
        self.assertIs(type(config.g), ConfigNode)
        # update with keyword argument
        config.update(k={})
        self.assertIs(type(config.k), ConfigNode)
        # update with iterable
        config.update([('m', {})])
        self.assertIs(type(config.m), ConfigNode)
        def fix_and_update():
            config.fixed_tree = True
            config.update(n=25)
        self.assertRaises(FixedTreeError, fix_and_update)

    def test_nested_update(self):
        config = Config(self._template)
        config.update(dict(b=dict(d=dict(f=25))))
        self.assertIs(type(config.b), ConfigNode)
        self.assertIs(type(config.b.d), ConfigNode)
        self.assertEqual(25, config.b.d.f)
        def fix_and_update():
            config.fixed_tree = True
            config.update(dict(b=dict(d=dict(newkey='new value'))))
        self.assertRaises(FixedTreeError, fix_and_update)

    def test_key_constraints(self):
        config = Config(self._template)
        def set_illegal_key():
            config[".*$"] = 25
        self.assertRaises(KeyError, set_illegal_key)
