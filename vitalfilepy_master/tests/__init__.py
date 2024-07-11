"""
Initialzation for tests.
Insert the src directory to module search path, so that
we can use import modules properly
"""
import sys
import os
testdir = os.path.dirname(__file__)
srcdir = '../src/'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
