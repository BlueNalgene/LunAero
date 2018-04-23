#!/usr/bin/python

"""Barebones recording script
Enables viewing of things from the picamera
Some arguments require certain programs
"""
import thread
import time
import picamera

def main():
	killkey = []
	thread.start_new_thread(innit, (killkey,))
	cam = picamera.PiCamera()
	cam.start_preview(fullscreen=False)
	while True:
		time.sleep(0.1)
		if killkey:
			break
	cam.stop_preview()

def innit(killkey):
	raw_input("Press any key to close preview...")
	killkey.append(None)

if __name__ == '__main__':
	main()
