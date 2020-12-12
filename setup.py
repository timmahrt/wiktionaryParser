#!/usr/bin/env python
# encoding: utf-8
'''
Created on Dec 12, 2020

@author: tmahrt
'''
from setuptools import setup
import io
setup(name='wiktionaryparser',
      version='1.0.0',
      author='Tim Mahrt',
      author_email='timmahrt@gmail.com',
      url='https://github.com/timmahrt/wiktionaryParser',
      package_dir={'wiktionaryparser':'wiktionaryparser'},
      packages=['wiktionaryparser',
                'wiktionaryparser.utilities'],
      license='LICENSE',
      description='A library for parsing wiktionary pages to get pronunciations and definitions.',
      long_description=io.open('README.md', 'r', encoding="utf-8").read(),
      long_description_content_type="text/markdown",
#       install_requires=[], # No requirements! # requires 'from setuptools import setup'
      )
