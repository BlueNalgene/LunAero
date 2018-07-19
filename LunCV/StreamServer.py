#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Server socket program for LunAero.  Listens for events from Client.
'''

import fcntl
import struct
import socket
#import sys
import time
#from io import BytesIO
#from threading import *
import pygame
#import pygame.camera
#from pygame.locals import *
from PIL import Image


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
		if data == "hats":
			break

###################################################################################################

def recv_robust(servsock, timeout):
	'''A robust recv method which amalgamates timeout, and end of message checks.
	It cannot do a message length check.
	'''

	# Empty variables
	#total_len = 0
	total_data = []
	data = ''
	#size = sys.maxint
	#size_data = sock_data = ''

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



	#while True:
		#data = servsock.recv(8192)
		#if not data:
			#break
		#total_data.append(data)
	#return ''.join(total_data)

#def recv_timeout(servsock, timeout=2):
	#'''Let's us know if we time out during TCP
	#'''

	## Declare that we are considering timeouts.
	#servsock.setblocking(False)

	## Empty variables
	#total_data = []
	#data = ''

	## Start counting the time
	#begin = time.time()

	#while 1:
		##if you got some data, then break after wait sec
		#if total_data and time.time()-begin > timeout:
			#break
		##if you got no data at all, wait a little longer
		#elif time.time()-begin > timeout*2:
			#break
		#try:
			#data = servsock.recv(8192)
			#if data:
				#total_data.append(data)
				#begin = time.time()
			#else:
				#time.sleep(0.1)
		#except socket.error:
			#pass
	#return ''.join(total_data)



#def recv_end(servsock):
	#'''Check for the end of the received message
	#'''

	## Empty variables
	#total_data = []
	#data = ''

	#while True:
		#data = servsock.recv(8192)
		#if endpoint in data:
			#total_data.append(data[:data.find(endpoint)])
			#break
		#total_data.append(data)
		#if len(total_data) > 1:
			##check if end_of_data was split
			#last_pair = total_data[-2]+total_data[-1]
			#if endpoint in last_pair:
				#total_data[-2] = last_pair[:last_pair.find(endpoint)]
				#total_data.pop()
				#break
	#return ''.join(total_data)

#def recv_size(servsock):
	#'''Determines the size of the packet which is being sent
	#data length is packed into 4 bytes
	#'''

	## Initialize empty variables
	#total_len = 0
	#total_data = []
	#size = sys.maxint
	#size_data = sock_data = ''

	## Recv packet size
	#recv_size = 8192
	#while total_len < size:
		#sock_data = servsock.recv(recv_size)
		#if not total_data:
			#if len(sock_data) > 4 or len(size_data) > 4:
				#size_data += sock_data
				#size = struct.unpack('>i', size_data[:4])[0]
				#recv_size = size
				#if recv_size > 524288:
					#recv_size = 524288
				#total_data.append(size_data[4:])
			#else:
				#size_data += sock_data
		#else:
			#total_data.append(sock_data)
		#total_len = sum([len(i) for i in total_data])
	#return ''.join(total_data)

server()


#def server():
	#try:
		#print "Server started at" + str(socket.gethostbyname(socket.gethostname())) + "at port 90"
		#port = 90
		#serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#serversocket.bind(("",port))
		##buffer, client_addr = socket.recvfrom(1024)
		##socket.sendto(some_buffer, client_addr)
		#serversocket.listen(10)
		#pygame.camera.init()
		#cam = pygame.camera.Camera(0,(640,480),"RGB")
		#cam.start()
		#img = pygame.Surface((640,480))
		#while True:
			#connection, address = serversocket.accept()
			#print "GOT_CONNECTION"
			#cam.get_image(img)
			#data = pygame.image.tostring(img,"RGB")
			#connection.sendall(data)
			#connection.close()
	#except:
		#pass

#server()
