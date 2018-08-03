#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Contains class for client commands for LunAero server
'''

import socket

import pygame

class Lclient():
	'''Class for client commands for LunAero server
	'''

	ip_address = '192.168.42.1'
	port = 90
	clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def __init__(self):
		'''intialize the class
		'''
		print("using Lclient")
		clientsocket = self.clientsocket
		clientsocket.settimeout(5)
		try:
			clientsocket.connect((self.ip_address, self.port))
			#return True
		except socket.error:
			print("Connection failure, retry")
			#return False

	def recv(self):
		'''Socket recieve function which processes images provided by the video stream
		'''
		clientsocket = self.clientsocket
		buffsize = 1024
		data = b''
		if self.connect_test:
			while True:
				if len(data) < 921600:
					recvd_data = clientsocket.recv(buffsize) #need 921600
					data += recvd_data
				else:
					image = pygame.image.fromstring(data, (640, 480), 'RGB') #image from bytes
					data = b''
					pygame.image.save(image, "tmp.jpg")
					return image

	def sendout(self, bytestring):
		'''Sends a string through the socket to the server to run a command on the remote Pi
		Current Command List:
		t = threshold down
		T = threshold up
		i = ISO cycle
		e = exposure down
		E = exposure up
		B = stop motors
		w = up
		a = left
		s = down
		d = right
		'''
		#clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientsocket = self.clientsocket
		clientsocket.sendall(bytestring)
		#if not ack:
			#self.sendto(bytestring)

	def sendrecv(self, bytestring):
		'''Sends a string through the socket to the server to run a command on the remote Pi
		then waits for a response
		'''

		clientsocket = self.clientsocket
		clientsocket.sendall(bytestring)
		print("I sent ", bytestring)

		length = None
		message = None
		buffer = ""

		while True:
			try:
				data = clientsocket.recv(4096)
				if not data:
					print("nothing yet boss")
					break
				buffer += data.decode('UTF-8')
				while True:
					if length is None:
						if ':' not in buffer:
							break
						message, _, buffer = buffer.partition(':')
						length = len(message)
					if len(buffer) > length:
						break
					if message == 'A':
						self.recv()
					print("I read ", message)
					return message
			except socket.timeout:
				print("timeout")
				return

	def connect_test(self):
		'''A simple test to detect if the socket is still connected
		'''
		clientsocket = self.clientsocket
		try:
			clientsocket.sendall("testdata")
			return True
		except socket.error:
			print("not connected")
			return False
