# This is a test program for the LunAero project which is able to:
#  - Locate the moon or a simulated moon
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen


# Includes code from speed-cam.py by Calude Pageau
# https://github.com/pageauc/rpi-speed-camera/tree/master/

#-----------------------------------------------------------------------------------------------

# Package Imports
import numpy as np 
import cv2 #OpenCV
import time
from time import sleep
import RPi.GPIO as GPIO #RPi GPIO controller
#from picamera.array import PiRGBArray #RPi Camera
from picamera import PiCamera #RPi Camera

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT) # A PWM
GPIO.setup(12, GPIO.OUT) # A input 2
GPIO.setup(13, GPIO.OUT) # A input 1
GPIO.setup(15, GPIO.OUT) # B input 1
GPIO.setup(16, GPIO.OUT) # B input 2
GPIO.setup(18, GPIO.OUT) # B PWM

# Start GPIO with 'off' values
GPIO.output(11, GPIO.HIGH)
GPIO.output(12, GPIO.LOW)
GPIO.output(13, GPIO.LOW)
GPIO.output(15, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(18, GPIO.HIGH)

# Location of movie file if using a pre-captured simulation or training video
# NOTE: If you have a Pi Camera attached to your RPi, it will use it before using 'cap'
cap = cv2.VideoCapture('testmoonvie.mov')


#-----------------------------------------------------------------------------------------------

try:
	while(cap.isOpened()):
	    TB66.horzOFF()
	    TB66.vertOFF()
	    ret, frame = cap.read()
	    
	    #Defines some important things
	    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	    thresh = 127
	    maxValue = 255
	    
	    if ret:
	        # The frame is ready and already captured
	        #cv2.imshow('frame', gray)
	        
	        #This determines the frame number
	        #pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
	        #print str(pos_frame)+" frames"
	        
	        #This is the meat.  It processes the grayscale'd frame for contours based on the threshold info.
	        th, dst = cv2.threshold(gray, thresh, maxValue, cv2.THRESH_BINARY);
	        contours,hierarchy=cv2.findContours(dst,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	        dst = cv2.cvtColor( dst, cv2.COLOR_GRAY2BGR )
	        #Then we draw the contour on the color original
	        cv2.drawContours(frame,contours,-1,(255,255,0),3)
	        
	        #Considers the first contour detected in a frame.
	        cnt = contours[0]
	        
	        #Determines the moments of the contoured shape in the frame, and their XY coordinate
	        M = cv2.moments(cnt)
	        cx = int(M['m10']/M['m00'])
	        cy = int(M['m01']/M['m00'])
	        
	        #Math to determine roundness
	        #area = cv2.contourArea(cnt)
	        #peri = cv2.arcLength(cnt,True)
	        #arrr = peri/(2*np.pi)
	        #print str(cx) + " and " + str(cy) + " and " + str(height) + "," + str(width)
	        
	        height, width, channels = frame.shape
	        whalf = width/2
	        hhalf = height/2
	        
	        #Check which how motors need to move to put moon in center
	        if cx < whalf:
			print "pan camera RIGHT"
			TB66.horzCW()
			sleep(0.05)
			GPIO.output(13, GPIO.LOW)
	        elif cx > whalf:
			print "pan camera LEFT"
			GPIO.output(15, GPIO.HIGH)
			sleep(0.05)
			GPIO.output(15, GPIO.LOW)
	        else:
			print "Center X"
	        if cy < hhalf:
			print "pan camera DOWN"
			GPIO.output(16, GPIO.HIGH)
			sleep(0.05)
			GPIO.output(16, GPIO.LOW)
	        elif cy > hhalf:
			print "pan camera UP"
			GPIO.output(18, GPIO.HIGH)
			sleep(0.05)
			GPIO.output(18, GPIO.LOW)
	        else:
			print "Center Y"
	        #cv2.imshow("Contour",frame
	    else:
	        # The next frame is not ready, so we try to read it again
	        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
	        print "frame is not ready"
	        # It is better to wait for a while for the next frame to be ready
	        cv2.waitKey(1000)
	    
	    if cv2.waitKey(1) & 0xFF == ord('q'):
	        break
except KeyboardInterrupt:
	GPIO.cleanup()
cap.release()
GPIO.cleanup()
cv2.destroyAllWindows()

#-----------------------------------------------------------------------------------------------
class TB66:
    def vertCW():
        # PWM on 1 high 2 low
        GPIO.output(13, GPIO.LOW) #1
        GPIO.output(12, GPIO.HIGH) #2
        GPIO.output(11, GPIO.HIGH) #pwm

    def horzCW():
        GPIO.output(15, GPIO.LOW) #1
        GPIO.output(16, GPIO.HIGH) #2
        GPIO.output(18, GPIO.HIGH) #pwm

    def vertCCW():
        # PWM on 1 high 2 low
        GPIO.output(13, GPIO.HIGH) #1
        GPIO.output(12, GPIO.LOW) #2
        GPIO.output(11, GPIO.HIGH) #pwm

    def horzCCW():
        GPIO.output(15, GPIO.HIGH) #1
        GPIO.output(16, GPIO.LOW) #2
        GPIO.output(18, GPIO.HIGH) #pwm

    def vertBrake():
        # PWM on 1 high 2 low
        GPIO.output(13, GPIO.HIGH) #1
        GPIO.output(12, GPIO.HIGH) #2
        GPIO.output(11, GPIO.LOW) #pwm

    def horzBrake():
        GPIO.output(15, GPIO.HIGH) #1
        GPIO.output(16, GPIO.HIGH) #2
        GPIO.output(18, GPIO.LOW) #pwm

    def vertOFF():
        # PWM on 1 high 2 low
        GPIO.output(13, GPIO.LOW) #1
        GPIO.output(12, GPIO.LOW) #2
        GPIO.output(11, GPIO.HIGH) #pwm

    def horzOFF():
        GPIO.output(15, GPIO.LOW) #1
        GPIO.output(16, GPIO.LOW) #2
        GPIO.output(18, GPIO.HIGH) #pwm

#-----------------------------------------------------------------------------------------------
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


