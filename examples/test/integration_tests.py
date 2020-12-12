#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Dec 12, 2020

@author: tmahrt

Runs integration tests

The examples were all written as scripts.  They weren't meant to be
imported or run from other code.  So here, the integration test is just
importing the scripts, which causes them to execute.  If the code completes
with no errors, then the code is at least able to complete.
'''

import unittest
import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
_root = os.path.split(cwd)[0]
sys.path.append(_root)

class IntegrationTests(unittest.TestCase):
    """Integration tests"""

    def test_page_debugger(self):
        """Running 'page_debugger.py'"""
        import page_debugger

    def setUp(self):
        unittest.TestCase.setUp(self)

        root = os.path.join(_root, "files")
        self.oldRoot = os.getcwd()
        os.chdir(_root)
        self.startingList = os.listdir(root)
        self.startingDir = os.getcwd()
    
    def tearDown(self):
        '''Remove any files generated during the test'''
        #unittest.TestCase.tearDown(self)
        
        root = os.path.join(".", "files")
        endingList = os.listdir(root)
        endingDir = os.getcwd()
        rmList = [fn for fn in endingList if fn not in self.startingList]
        
        if self.oldRoot == root:
            for fn in rmList:
                fnFullPath = os.path.join(root, fn)
                if os.path.isdir(fnFullPath):
                    os.rmdir(fnFullPath)
                else:
                    os.remove(fnFullPath)
        
        os.chdir(self.oldRoot)

if __name__ == '__main__':
    unittest.main()
