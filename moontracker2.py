#!/bin/usr/python3 -B

import sys
import subprocess
import os
import os.path
from scipy import ndimage
from PIL import Image
import numpy as np
import pygame, sys
import RPi.GPIO as GPIO
import time
import picamera
#import matplotlib.pyplot as plt

moveFactorX = 0.0020 
moveFactorY = 0.0015
lostRatio = 0.01

lostCount = 0 #Always initialize at 0
start = time.time()


# a percentage of frame height
# the moon must be displaced by this amount for movement to occur.
MOVETHRESH = 0.05

white = (255,255,255)
# Defines the pins being used for the GPIO pins.
print ("Defining GPIO pins")
GPIO.setmode(GPIO.BCM)
XPINP = 17
XPIN1 = 27
XPIN2 = 22
YPIN1 = 10
YPIN2 = 9
YPINP = 11

# Setup GPIO and start them with 'off' values
PINS = (XPIN1, XPIN2, XPINP, YPIN1, YPIN2, YPINP)
for i in PINS:
	GPIO.setup(i, GPIO.OUT)
	if i != XPINP or YPINP:
		GPIO.output(i, GPIO.LOW)
	else:
		GPIO.output(i, GPIO.HIGH)
		
##freq = 1000
##pwmA = GPIO.PWM(XPINP, freq)   # Initialize PWM on pwmPin 
##pwmB = GPIO.PWM(YPINP, freq) 
##dc=0                          # set dc variable
##pwmA.start(dc)                      
##pwmB.start(dc) 


def motStop():
    print("stopping")
    GPIO.output(XPIN1, GPIO.LOW)
    GPIO.output(XPIN2, GPIO.LOW)
    GPIO.output(YPIN1, GPIO.LOW)
    GPIO.output(YPIN2, GPIO.LOW)
    GPIO.output(YPINP, GPIO.LOW)
    GPIO.output(XPINP, GPIO.LOW)
    return

def motUp():
    print("moving up")
    GPIO.output(XPIN1, GPIO.HIGH)
    GPIO.output(XPIN2, GPIO.LOW)
    GPIO.output(XPINP, GPIO.HIGH)
    return

def motDown():
    print("moving down")
    GPIO.output(XPIN1, GPIO.LOW)
    GPIO.output(XPIN2, GPIO.HIGH)
    GPIO.output(XPINP, GPIO.HIGH)
    return

def motLeft():
    print("moving left")
    GPIO.output(YPIN1, GPIO.HIGH)
    GPIO.output(YPIN2, GPIO.LOW)
    GPIO.output(YPINP, GPIO.HIGH)
    return

def motRight():
    print("moving right")
    GPIO.output(YPIN1, GPIO.LOW)
    GPIO.output(YPIN2, GPIO.HIGH)
    GPIO.output(YPINP, GPIO.HIGH)
    return

def startRecording():
    global start
    start = time.time()
    print(start)
    print ("Preparing outfile")
    outfile = int(time.time())
    outfile = str(outfile) + 'outA.h264'
    outfile = os.path.join('/media/pi/MOON1', outfile)
    print (str(outfile))
    camera.start_recording(outfile)
    time.sleep(1)



camera = picamera.PiCamera()
camera.resolution = (1920, 1080)
camera.color_effects = (128,128) # turn camera to black and white
camera.start_preview(fullscreen = False, window = (600,-20,1280,960))

pygame.init()
pygame.display.set_caption('Manual control')
size = [400, 240]
screen = pygame.display.set_mode(size)
font = pygame.font.SysFont('Arial', 25)
screen.blit(font.render('Use arrow keys to move.', True, (255,0,0)), (25, 25))
screen.blit(font.render('Hit the space bar to stop.', True, (255,0,0)), (25, 75))
screen.blit(font.render('Press ENTER or r to run the', True, (255,0,0)), (25, 125))
screen.blit(font.render('moon tracker', True, (255,0,0)), (25, 165))
pygame.display.update()
clock = pygame.time.Clock()
x = 0

while x < 10:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            motStop()
            x = 100   
        # check if key is pressed
        # if you use event.key here it will give you error at runtime
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                print("left")
                motLeft()     
            if event.key == pygame.K_RIGHT:
                print("right")
                motRight()
            if event.key == pygame.K_UP:
                print("up")
                motUp()
            if event.key == pygame.K_DOWN:
                print("down")
                motDown()
            if event.key == pygame.K_SPACE:
                print("space")
                motStop()
            if event.key == pygame.K_r:
                print("run tracker")
                motStop()
                x = 100
            if event.key == pygame.K_RETURN:
                print("run tracker")
                motStop()
                x = 100
#pygame.quit()
#GPIO.cleanup()
print("quitting manual control, switching to tracking")
#sys.exit()
#print("continue")
#pygame.display.quit()

screen.fill((0,0,0))
pygame.display.update()
pygame.display.set_caption('Tracking Moon')
screen.blit(font.render('TRACKING MOON.', True, (255,0,0)), (25, 25))
screen.blit(font.render('Click this window and type "q" to quit', True, (255,0,0)), (25, 75))
screen.blit(font.render('Or just close this window to to quit.', True, (255,0,0)), (25, 125))
screen.blit(font.render('(it might take a few seconds)', True, (255,0,0)), (25, 175))
pygame.display.update()


##print ("Preparing outfile")
##outfile = int(time.time())
##outfile = str(outfile) + 'outA.h264'
##outfile = os.path.join('/media/pi/MOON1', outfile)
##print (str(outfile))
##camera.start_recording(outfile)
##time.sleep(1)

startRecording()

cnt = 0
while cnt < 55:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                cnt = 100
        if event.type == pygame.QUIT:
            cnt = 100
    now = time.time()      #check the time to restart camera every hour or so
    timeCount = now - start
    camera.annotate_text = ' ' * 100 + str(int(round(timeCount))) + 'sec'
    if timeCount > 2*60*60:
        print("restart video")
        camera.stop_recording()
        startRecording()
            
    #Capture an image and see how close it is to center
    camera.capture('debugimage.jpg', use_video_port=True, resize=(640, 480))
    img = Image.open('debugimage.jpg')
    #img.show()
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 20 else 255, '1')
    img.save("tmp.png")
    os.system("xdg-open tmp.png") #display image - for debugging only
    time.sleep(1)
    ##os.system("fuser -k -TERM tmp.png")
    arm = np.asarray(img)


    width, height = img.size
    percent = height/100
    thresh = percent*MOVETHRESH
    cenx = width/2
    ceny = height/2
    cmy, cmx = ndimage.measurements.center_of_mass(arm)
    arm = arm.sum()
    ratio = arm/(width*height)
    print(arm, ratio, thresh, width, height, cmx, cmy)
    diffx = abs(cenx - cmx)
    diffy = abs(ceny - cmy)
    maxdiff = max(diffx, diffy)
    if ratio < lostRatio:
        print("moon lost")
        lostCount = lostCount + 1
        time.sleep(3)
        if lostCount > 15:
            print("moon totally lost")
            os.system("killall gpicview")
            break
    else:
        lostCount = 0
        if maxdiff/height < MOVETHRESH:
            print("don't move ", diffx, diffy, max(diffx, diffy), maxdiff)
            time.sleep(3)
        else:
            print(diffx, diffy, max(diffx, diffy))
            if diffx > diffy:
                print("move x")
                movetime = diffx * moveFactorX
                if cmx < cenx:
                    motLeft()
                else:
                    motRight()
            else:
                print("move y")
                movetime = diffy * moveFactorY
                if cmy < ceny:
                    motUp()
                else:
                    motDown()
            time.sleep(movetime)
            motStop()
    os.system("killall gpicview")
    #cnt = cnt + 1
    
       
time.sleep(2)
motStop()
camera.stop_recording()
os.system("killall gpicview")
camera.stop_preview()
pygame.quit() 
GPIO.cleanup()
