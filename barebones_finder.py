#!/usr/bin/python

"""Barebones recording script
Enables recording and viewing of things from the picamera
Some arguments require certain programs
"""

import argparse
from os import popen
import picamera

import caca

parser = argparse.ArgumentParser(prog='Barebones Finder for Raspberry Pi camera')
parser.description = "This is where the command-line utility's description goes."
parser.epilog = "This is where the command-line utility's epilog goes."

parser.add_argument('-h', 
					'--help',
					help='Displays this help info.')
parser.add_argument('-o',
					'--output',
					nargs='1',
					help='Specifies output file',
					type=str)
parser.add_argument('-a',
					'--ascii',
					help='Sets viewing mode to text based pseudo-image.')
args = parser.parse_args()



cam = picamera.PiCamera()
cam.start_preview(fullscreen=False, window(100, 20, 640, 480)


with open(args.output, 'w') as output_file:
    output_file.write("%s\n" % item)
