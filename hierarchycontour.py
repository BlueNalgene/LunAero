# This is a test program for the LunAero project which is able to:
#  - Locate a simplified moon
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen

#This particular file deals with hierarchy

import numpy as np
import cv2

#cap = cv2.VideoCapture('statmoonwbirds.mov')
cap = cv2.VideoCapture('Migrants.mp4')
#cap = cv2.VideoCapture('Nocturnal.mp4')

#This is the background removing step
fgbg = cv2.BackgroundSubtractorMOG(100,7,0.5,5)

#This defines a matrix for other functions
mat = np.ones((3,3),np.uint8)

try:
    while(cap.isOpened()):
        ret, frame = cap.read()
        
        # learningRate = 0.05 deals with moon features better, but may be too taxing for Pi
        fgmask = fgbg.apply(frame, learningRate=.1)
        
        #Defines some important things
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #This is where any image manipulation happens
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        can = cv2.Canny(blurred, 5, 200)
        fgmask = cv2.addWeighted(fgmask,0.5,can,0.5,0)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_GRADIENT, mat)
        
        # This if loop detects the contours in the manipulated image and displays
        if ret:
            
            #ret,thresh = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)
            #contours,hierarchy = cv2.findContours(thresh, 3, 2)
            #nocolor = cv2.cvtColor(fgmask, cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(fgmask,0,255,cv2.THRESH_BINARY)
            contours,hierarchy = cv2.findContours(thresh, 3, 2)

            #This if is required to ignore initial frames
            if not contours:
                pass
            else:

                cnt = contours[0]
                i = 0
            
                # Three different hierarchal levls get circled in different colors
                for cnt in contours:
                    if hierarchy[0][i][3] == (-1):
                        (x,y),radius = cv2.minEnclosingCircle(cnt)
                        center = (int(x),int(y))
                        radius = int(radius)
                        cv2.circle(frame,center,radius,(0,255,0),2)
                    elif hierarchy[0][i][3] == 0:
                        (x,y),radius = cv2.minEnclosingCircle(cnt)
                        center = (int(x),int(y))
                        radius = int(radius)
                        cv2.circle(frame,center,radius,(255,255,0),2)
                    elif hierarchy[0][i][3] <= 1:
                        (x,y),radius = cv2.minEnclosingCircle(cnt)
                        center = (int(x),int(y))
                        radius = int(radius)
                        cv2.circle(frame,center,radius,(0,0,255),2)
                    i = 1 + i
     
            # This mess displays different things side by side
            # The Mother window shows the manipulated image that is being used for cakculations
            # The Original window shows the contours overlaid on the original frame
            cv2.namedWindow("Mother", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Mother",700,500)
            cv2.imshow("Mother",fgmask)
            cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Original",700,500)
            cv2.imshow("Original",frame)
        else:
            # The next frame is not ready, so we try to read it again
            cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
            print "frame is not ready"
            # It is better to wait for a while for the next frame to be ready
            cv2.waitKey(1000)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
