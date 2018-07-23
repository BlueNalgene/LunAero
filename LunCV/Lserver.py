#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Server socket program for LunAero.  Listens for events from Client.
'''

import fcntl
import struct
import socket
import time

import pygame
from pygame import camera

from PIL import Image
import CameraCommands as CC
import MotorControl

MC = MotorControl.MotorControl()

def get_ip_address(ifname):
	'''Get the ip address for your device using the SIOCGIFADDR method
	'''
	servsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sio = socket.inet_ntoa(fcntl.ioctl(servsocket.fileno(), 0x8915,\
		struct.pack('256s', ifname[:15]))[20:24])
	return sio

def server():
	'''Defines how to initialize the server
	'''
	servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = 90
	ip_address = get_ip_address('wlan0')
	servsock.bind((ip_address, port))
	servsock.listen(5)
	print("\nServer started at " + str(ip_address) + " at port " + str(port))

	pygame.camera.init()

	while True:
		servsock.listen(5)
		client_sock, _ = servsock.accept()
		data = client_sock.recv(20)
		if not data:
			break
		if data == "a":
			img = Image.open('tmp.png')
			img = img.resize(img)
			imgbyte = img.tobytes()
			#len for 640x480 bytes is 921600
			client_sock.sendall(imgbyte)
			break
		if data == 't':
			CC.thresh_dec()
			break
		if data == 'T':
			CC.thresh_inc()
			break
		if data == 'i':
			CC.iso_cyc()
			break
		if data == 'e':
			CC.exp_dec()
			break
		if data == 'E':
			CC.exp_inc()
			break
		if data == 'B':
			MC.mot_stop("B")
			break
		if data == 'w':
			MC.pwmb.ChangeDutyCycle(100)
			MC.mot_up()
			break
		if data == 'a':
			MC.pwma.ChangeDutyCycle(100)
			MC.mot_left()
			break
		if data == 's':
			MC.pwmb.ChangeDutyCycle(100)
			MC.mot_down()
			break
		if data == 'd':
			MC.pwma.ChangeDutyCycle(100)
			MC.mot_right()
			break
def recv_robust(servsock, timeout):
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

server()
