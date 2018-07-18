#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Server socket program for LunAero.  Listens for events from Client.
'''

import fcntl
import struct
import socket
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
		img = Image.open('tmp.png')
		img = img.resize(img)
		imgbyte = img.tobytes()
		#len for 640x480 bytes is 921600
		client_sock, _ = servsock.accept()
		client_sock.sendall(imgbyte)

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
