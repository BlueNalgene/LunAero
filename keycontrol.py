#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

import pygame, sys
import RPi.GPIO as GPIO
import time
import picamera

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

camera = picamera.PiCamera()
camera.color_effects = (128,128) # turn camera to black and white
camera.start_preview(fullscreen = False, window = (700,-20,640,480))

pygame.init()
pygame.display.set_caption('Manual control')
size = [640, 480]
screen = pygame.display.set_mode(size)
font = pygame.font.SysFont('Arial', 35)
screen.blit(font.render('Use arrow keys to move.', True, (255,0,0)), (50, 100))
screen.blit(font.render('Hit the space bar to stop.', True, (255,0,0)), (50, 150))
screen.blit(font.render('Close the window to end program.', True, (255,0,0)), (50, 200))
pygame.display.update()
clock = pygame.time.Clock()
 
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
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

    #screen.fill(white)
 
    #pygame.display.update()
    clock.tick(20)

camera.stop_preview()
GPIO.cleanup()
    
