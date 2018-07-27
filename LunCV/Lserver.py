#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Server socket program for LunAero.  Listens for events from Client.
'''

import fcntl
import os
import struct
import socket
import time
import traceback

import pygame
from pygame import camera

from PIL import Image
import CameraCommands as CC
import MotorControl

MC = MotorControl.MotorControl()

class Lserver():
	'''Server socket program for LunAero.  Listens for events from Client.
	'''

	servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	prev = 3

	def get_ip_address(self, ifname):
		'''Get the ip address for your device using the SIOCGIFADDR method
		'''
		servsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sio = socket.inet_ntoa(fcntl.ioctl(servsocket.fileno(), 0x8915,\
			struct.pack('256s', ifname[:15]))[20:24])
		return sio

	def server(self):
		'''Defines how to initialize the server
		'''
		servsock = self.servsock
		port = 90
		ip_address = self.get_ip_address('wlan0')
		servsock.bind((ip_address, port))
		servsock.listen(5)
		print("\nServer started at " + str(ip_address) + " at port " + str(port))

		pygame.camera.init()

		while True:
			servsock.listen(5)
			client_sock, _ = servsock.accept()
			data = client_sock.recv(20)
			#if not data:
				#break
			if data == "a":
				img = Image.open('tmp.png')
				img = img.resize(img)
				imgbyte = img.tobytes()
				#len for 640x480 bytes is 921600
				client_sock.sendall(imgbyte)

			if data == 't':
				CC.thresh_dec()

			if data == 'T':
				CC.thresh_inc()

			if data == 'i':
				CC.iso_cyc()

			if data == 'e':
				CC.exp_dec()

			if data == 'E':
				CC.exp_inc()

			if data == 'B':
				MC.mot_stop("B")

			if data == 'w':
				MC.pwmb.ChangeDutyCycle(100)
				MC.mot_up()

			if data == 'a':
				MC.pwma.ChangeDutyCycle(100)
				MC.mot_left()

			if data == 's':
				MC.pwmb.ChangeDutyCycle(100)
				MC.mot_down()

			if data == 'd':
				MC.pwma.ChangeDutyCycle(100)
				MC.mot_right()

			if data == 'x':
				outfile = int(time.time())
				outfile = str(outfile) + 'outA.h264'
				if os.path.isdir('/media/pi/MOON1'):
					outfile = os.path.join('/media/pi/MOON1', outfile)
				else:
					print("Check that the thumbdrive is plugged in and mounted")
					print("You should see it at /media/pi/MOON1")
					if True:
						print("Continuing with a new save location")
						outfile = os.path.join('/home/pi/Documents', outfile)
					else:
						raise ValueError("The thumbdrive is not where I expected it to be!")
				print(str(outfile))
				CC.start_recording(outfile)
				time.sleep(1)

			if data == 'p':
				#TODO This function returns a value we might want
				self.prev = CC.go_prev(self.prev)
				client_sock.sendall((b'n', self.prev)

			if data == 'P':
				self.prev = self.prev + 1
				if self.prev > 5:
					self.prev = 1
				CC.stop_preview()
				CC.go_prev(self.prev)

	def recv_robust(self, servsock, timeout):
		'''A robust recv method which amalgamates timeout, and end of message checks.
		It cannot do a message length check.
		'''

		# Empty variables
		total_data = []
		data = ''

		# This is our end of message character.  Make sure it is a single character, so won't break up
		endpoint = '\0'

		# Declare that we are considering timeouts.
		servsock.setblocking(False)

		# Start counting the time
		begin = time.time()

		while True:
			#if you got some data, then break after wait sec
			if total_data and time.time()-begin > timeout:
				break
			#if you got no data at all, wait a little longer
			elif time.time()-begin > timeout*2:
				break
			try:
				data = servsock.recv(8192)
				if data:
					if endpoint in data:
						total_data.append(data[:data.find(endpoint)])
						break
					total_data.append(data)
					begin = time.time()
					if len(total_data) > 1:
						#check if end_of_data was split
						last_pair = total_data[-2]+total_data[-1]
						if endpoint in last_pair:
							total_data[-2] = last_pair[:last_pair.find(endpoint)]
							total_data.pop()
							break
						else:
							time.sleep(0.1)
			except socket.error:
				pass
		return ''.join(total_data)


L = Lserver()
try:
	L.server()
except Exception as inst:
	print("Exception Type: ", type(inst))
	print("Exception Args: ", inst.args)
	print("Exception     : ", inst)
	traceback.print_exc()
finally:
	CC.shutdown_camera()
	os.system("killall gpicview")
