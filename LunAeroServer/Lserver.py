#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Server socket program for LunAero.  Listens for events from Client.
'''

import fcntl
import os
import struct
import socket
import threading
import time
import traceback

import pygame
from pygame import camera

from PIL import Image
import CameraCommands
import MotorControl

CC = CameraCommands.CameraCommands()
MC = MotorControl.MotorControl()

class Lserver():
	'''Server socket program for LunAero.  Listens for events from Client.
	'''

	servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	prev = 3

	def get_ip_address(self, ifname):
		'''Get the ip address for your device using the SIOCGIFADDR method
		'''
		ifname = bytes(ifname[:15], encoding='UTF-8')
		ifreq = struct.pack('256s', ifname)
		sio = socket.inet_ntoa(fcntl.ioctl(self.servsock.fileno(), 0x8915, ifreq)[20:24])
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
		client_sock, _ = servsock.accept()

		try:
			capthread = threading.Thread(target=CC.stream_cap)
			capthread.start()

			length = None
			message = None
			buffer = ""

			while True:
				data = client_sock.recv(1024)
				if not data:
					break
				buffer += data.decode('UTF-8')
				while True:
					if length is None:
						if ':' not in buffer:
							break
						message, _, buffer = buffer.partition(':')
						length = len(message)

						# Message Tree

						if message == "A":
							client_sock.sendall(b'A:')
							img = Image.open('/var/tmp/LunAero/tmp.jpg')
							img = img.resize([640, 480])
							imgbyte = img.tobytes()
							#len for 640x480 bytes is 921600
							client_sock.sendall(imgbyte)

						if message == 't':
							CC.thresh_dec()

						if message == 'T':
							CC.thresh_inc()

						if message == 'i':
							iso = CC.iso_cyc()
							iso = str(iso)
							iso += ':'
							iso = bytes(iso, encoding='UTF-8')
							client_sock.sendall(iso)

						if message == 'e':
							CC.exp_dec()

						if message == 'E':
							CC.exp_inc()

						if message == 'B':
							MC.mot_stop("B")

						if message == 'w':
							MC.pwmb.ChangeDutyCycle(100)
							MC.mot_up()

						if message == 'a':
							MC.pwma.ChangeDutyCycle(100)
							MC.mot_left()

						if message == 's':
							MC.pwmb.ChangeDutyCycle(100)
							MC.mot_down()

						if message == 'd':
							MC.pwma.ChangeDutyCycle(100)
							MC.mot_right()

						if message == 'x':
							outfile = int(time.time())
							outfile = str(outfile) + 'outA.h264'
							if os.path.isdir('/media/pi/MOON1'):
								outfile = os.path.join('/media/pi/MOON1', outfile)
							else:
								print("Check that the thumbdrive is plugged in and mounted")
								print("You should see it at /media/pi/MOON1")
								print("Continuing with a alt location (/home/pi/Documents)")
								outfile = os.path.join('/home/pi/Documents', outfile)
							print(str(outfile))
							CC.start_recording(outfile)
							time.sleep(1)

						if message == 'p':
							prev = CC.go_prev(self.prev)
							prev = str(prev)
							prev += ':'
							prev = bytes(prev, encoding='UTF-8')
							client_sock.sendall(prev)

						if message == 'P':
							self.prev = self.prev + 1
							if self.prev > 5:
								self.prev = 1
							CC.stop_preview()
							CC.go_prev(self.prev)

						if message == 'R':
							from Lconfig import VERTTHRESHSTART, HORTHRESHSTART, LOSTRATIO

							diffx, diffy, ratio, cmx, cmy = CC.get_img()
							print(ratio, cmx, cmy, diffx, diffy)

							if (abs(diffy) > VERTTHRESHSTART or abs(diffx) > HORTHRESHSTART):
								check = CC.checkandmove()

							lost_count = 0
							if check == 1:       #Moon successfully centered
								print("centered")
								lost_count = 0

								os.system("xdg-open tmp.jpg") #display image - for debugging only
								time.sleep(3)
								os.system("killall gpicview")

							if check == 0:       #centering in progress
								time.sleep(.02)  #sleep for 20ms
							if (check == 2 or ratio < LOSTRATIO):#moon lost, theshold too low
								lost_count = lost_count + 1
								print("moon lost")
								time.sleep(1)
								if lost_count > 30:
									print("moon totally lost")
									cnt = '1:'
									cnt = bytes(cnt, encoding='UTF-8')
									client_sock.sendall(cnt)
									return
							cnt = '0:'
							cnt = bytes(cnt, encoding='UTF-8')
							client_sock.sendall(bytestring)
							return

						if message == 'r':
							conf = '1:'
							conf = bytes(conf, encoding='UTF-8')
							client_sock.sendall(conf)
							while True:
								data = client_sock.recv(4096)
								if not data:
									print("nothing yet boss")
									break
								buffer += data.decode('UTF-8')
								print("I got ", buffer)
								while True:
									if length is not None:
										if ':' not in buffer:
											break
										message, _, buffer = buffer.partition(':')
										length = len(message)
									if len(buffer) > length:
										break
									start = float(message[1:])
									start = CC.timed_restart(start)
									start = str(start)
									start += ':'
									start = bytes(start, encoding='UTF-8')
									client_sock.sendall(start)
									return

					length = None
					message = None
		finally:
			capthread.join()

L = Lserver()
try:
	L.server()
except Exception as inst:
	if inst == OSError:
		print("had an OSError, FYI")
		pass
	elif inst == KeyboardInterrupt:
		print("KeyboardInterrupt")
	else:
		print("Exception Type: ", type(inst))
		print("Exception Args: ", inst.args)
		print("Exception     : ", inst)
		traceback.print_exc()
finally:
	print("Shutting Down")
	CC.shutdown_camera()
	MC.cleanup()
	os.system("killall gpicview")
