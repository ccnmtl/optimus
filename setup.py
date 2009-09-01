#!/usr/bin/python

from distutils.core import setup
import re,sys,os,Image,ImageTk,Tkinter,tkFileDialog,tkSimpleDialog,Numeric
import urllib,xml.dom.minidom,csv
from Organizer import Organizer
from Federate import Federate
from OptimusEvent import OptimusEvent
from FedMenu import FedOpener,AttMenu
try: 
	import py2exe
except: 
	print "couldn't import py2exe"

import glob

setup(name="optimus",
        console=["Optimus.py"],
        scripts=["Optimus.py","street_layout_tool.py","dijkstra.py"]) 
