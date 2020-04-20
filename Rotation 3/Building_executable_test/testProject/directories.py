# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 11:14:55 2018

@author: 212566876
"""

import sys, os
frozen = 'not'
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
print( 'we are',frozen,'frozen')
print( 'bundle dir is', bundle_dir )
print( 'sys.argv[0] is', sys.argv[0] )
print( 'sys.executable is', sys.executable )
print( 'os.getcwd is', os.getcwd() )
print( 'os.path.dirname(sys.executable) is', os.path.dirname(sys.executable))
endProgram = input('Press RETURN to exit the console')