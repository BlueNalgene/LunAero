#!/usr/bin/python

"""
# This is a test program for the LunAero project which is able to:
#  - Locate the moon or a simulated moon from a sample image
#  - Track the motion of the moon from the center of the screen
#  - Record video of the process

"""

import time
import sys
import subprocess
import os
import os.path

import picamera
from scipy import ndimage
from PIL import Image
import numpy as np
import RPi.GPIO as GPIO

### USER ALTERABLE VARIABLES ###
# Enable a debugging mode that shows more verbose info
DEBUG = False
# Number of seconds to delay between sampling frames.
DELAY = 0.01
# a percentage of frame height
# the moon must be displaced by this amount for movement to occur.
MOVETHRESH = 10
# This defines the maximum duty cycle for the motor
# It must be a number from 1-100
# Default 100, lower to slow the motors
DUTY = 100
# This is the PWM frequency for the motors (units of Hz)
FREQ = 10000

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
	

def main():
    CAM = picamera.PiCamera()	
    try:
        
        CAM.resolution = (1920, 1080)
        CAM.color_effects = (128,128) # turn camera to black and white
        CAM.start_preview(fullscreen = False, window = (700,-20,640,480))
        CAM.start_recording(outfile)
        time.sleep(3)
        while True:
            CAM.capture('debugimage.jpg', use_video_port=True, resize=(640, 480))
            time.sleep(1)
            img = Image.open('debugimage.jpg')
            img = img.convert('L')
            img = img.point(lambda x: 0 if x < 128 else 255, '1')
            img.save("tmp.png")
            #os.system("xdg-open tmp.png") #display image - for debugging only
            arm = np.asarray(img)

            width, height = img.size
            percent = height/100
            thresh = percent*MOVETHRESH
            cenx = width/2
            ceny = height/2
            cmy, cmx = ndimage.measurements.center_of_mass(arm)

            #Are there sufficient pixels to work with?
            arm = arm.sum()
            if DEBUG:
                print(arm)
            ratio = arm/(width*height)
            if DEBUG:
                print(arm, ratio, thresh, width, height, cmy, cmx)

            #Conditional (if) for ending program if ratio is too low
            
            durationx = 0
            durationy = 0 
            if cmx + thresh < cenx:
                durationx = DELAY*(cenx-cmx) #how long to run motor
                if DEBUG:
                    print("pan camera LEFT for ", durationx)
                mot_left()
                time.sleep(0.2)
            if cmx - thresh > cenx:
                durationx = DELAY*(cmx-cenx)
                if DEBUG:
                    print("pan camera RIGHT for ", durationx)
                mot_right()
            if cmy + thresh < ceny:
                durationy = DELAY*(ceny-cmy)
                if DEBUG:
                    print("pan camera UP for ", durationy)
                mot_up()
            if cmy - thresh > ceny:
                durationy = DELAY*(cmy-ceny)
                if DEBUG:
                    print("pan camera DOWN for ", durationy)
                mot_down()

            if durationx == 0 and durationy == 0:
                if DEBUG:
                    print("No need to move")
                time.sleep(5)
            else:
                if durationx < durationy:
                    diff = durationy - durationx
                    if DEBUG:
                        print(durationx, diff)
                    time.sleep(durationx)
                    if durationx > 0:
                        mot_stop_x()
                    time.sleep(diff)
                    mot_stop_y()
                else:
                    diff = durationx - durationy
                    time.sleep(durationy)
                    if durationy > 0:
                        mot_stop_y()
                    time.sleep(diff)
                    mot_stop_x()
    except Exception as exep:
        exep = sys.exc_info()[0]
        print ('\033[91m'+ "Error: %s" % exep + '\033[0m')
        raise
        print("closing")
    finally:
        CAM.stop_recording()
        CAM.stop_preview()
        GPIO.cleanup()




def motStop():
    print("stopping")
    GPIO.output(XPIN1, GPIO.LOW)
    GPIO.output(XPIN2, GPIO.LOW)
    GPIO.output(YPIN1, GPIO.LOW)
    GPIO.output(YPIN2, GPIO.LOW)
    dc=0                            # set dc variable t
    pwmA.ChangeDutyCycle(dc)
    pwmB.ChangeDutyCycle(dc)	
    return

def mot_stop_x():
    print("stopping X")
    GPIO.output(XPIN1, GPIO.LOW)
    GPIO.output(XPIN2, GPIO.LOW)
    dc=0                            # set dc variable t
    pwmA.ChangeDutyCycle(dc)
    return

def mot_stop_y():
    print("stopping Y")
    GPIO.output(YPIN1, GPIO.LOW)
    GPIO.output(YPIN2, GPIO.LOW)
    dc=0                            # set dc variable t
    pwmB.ChangeDutyCycle(dc)	
    return

def mot_up():
    print("moving up")
    GPIO.output(XPIN1, GPIO.HIGH)
    GPIO.output(XPIN2, GPIO.LOW)
    dc=DUTY                          
    pwmA.ChangeDutyCycle(dc)
    return

def mot_down():
    print("moving down")
    GPIO.output(XPIN1, GPIO.LOW)
    GPIO.output(XPIN2, GPIO.HIGH)
    dc=DUTY                          
    pwmA.ChangeDutyCycle(dc)
    return

def mot_left():
    print("moving left")
    GPIO.output(YPIN1, GPIO.HIGH)
    GPIO.output(YPIN2, GPIO.LOW)
    dc=DUTY                          
    pwmB.ChangeDutyCycle(dc)
    return

def mot_right():
    print("moving right")
    GPIO.output(YPIN1, GPIO.LOW)
    GPIO.output(YPIN2, GPIO.HIGH)
    dc=DUTY                         
    pwmB.ChangeDutyCycle(dc)
    return

if __name__ == '__main__':
    pwmA = GPIO.PWM(XPINP, FREQ)   # Initialize PWM on pwmPin 
    pwmB = GPIO.PWM(YPINP, FREQ) 
    dc=0                          # set dc variable
    pwmA.start(dc)                      
    pwmB.start(dc) 
    
    # Sets up an output file labeled with the current unixtime
    print ("Preparing outfile")
    outfile = int(time.time())
    outfile = str(outfile) + 'outA.h264'
    outfile = os.path.join('/media/pi/MOON1', outfile)
    print (str(outfile))
    main()