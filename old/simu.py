# This is a test program for the LunAero project which is able to:
#  - Locate a simplified moon
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen

import numpy as np
import cv2

cap = cv2.VideoCapture('testmoonvie.mov')

while(cap.isOpened()):
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
        elif cx > whalf:
            print "pan camera LEFT"
        else:
            print "Center X"
        if cy < hhalf:
            print "pan camera DOWN"
        elif cy > hhalf:
            print "pan camera UP"
        else:
            print "Center Y"
        cv2.imshow("Contour",frame)
    else:
        # The next frame is not ready, so we try to read it again
        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
        print "frame is not ready"
        # It is better to wait for a while for the next frame to be ready
        cv2.waitKey(1000)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
