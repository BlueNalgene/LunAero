#!/usr/bin/python

"""Barebones recording script
Enables viewing of things from the picamera
Some arguments require certain programs
"""
import thread
import time
import picamera

killkey = []
thread.start_new_thread(innit, (L,))
cam = picamera.PiCamera()
cam.start_preview(fullscreen=False, window(100, 20, 640, 480))
while True:
	time.sleep(0.1)
	if L:
		break
cam.stop_preview()

def innit(killkey):
	raw_input("Press any key to close preview...")
	L.append(None)
