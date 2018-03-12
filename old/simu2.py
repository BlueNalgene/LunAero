# This is a test program for the LunAero project which is able to:
#  - Locate a simplified moon
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen

#This particular file deals with hierarchy

import numpy as np
import cv2

#cap = cv2.VideoCapture('statmoonwbirds.mov')
cap = cv2.VideoCapture('Migrants.mp4')

while(cap.isOpened()):
    ret, frame = cap.read()
    
    #Defines some important things
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = 1
    maxValue = 255
    
    if ret:
        # The frame is ready and already captured
        #cv2.imshow('frame', gray)
        
        #This determines the frame number
        #pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        #print str(pos_frame)+" frames"
        
        #This is the meat.  It processes the grayscale'd frame for contours based on the threshold info.
        th, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU);
        contours,hierarchy=cv2.findContours(dst,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        #dst = cv2.cvtColor( dst, cv2.COLOR_GRAY2BGR )
        #Then we draw the contour on the color original
        #cv2.drawContours(frame,contours,-1,(255,255,0),3)
        
        cnt = contours[0]
        tops = hierarchy[0][0:100][0:100][0][0]
        parent = [x[2] for x in hierarchy[0]]
        
        #for cnt in contours:
        
        #print "hierarchy = " + str(hierarchy)
        #print "listed = " + str(parent)
        #print "tops = " + str(tops)
        
        for cnt in contours:
            contourcount = len(parent)
            for i in parent:
                j = i + 1
                j = 255 + j * 255
                print "Found " + str(j)
                cv2.drawContours(frame,contours,i,j,3)
            
        
        #for i in parent:
            #if i == 1:
                #cv2.drawContours(frame,contours,-1,(0,255,0),3)
            #else:
                #cv2.drawContours(frame,contours,-1,(255,0,255),3)

        #print zip(contours,hierarchy)
        
        #if tops == 1:
            #cv2.drawContours(frame,contours,-1,(0,255,255),3)
            #print hierarchy[0]
        #else:
            #cv2.drawContours(frame,contours,-1,(255,0,255),3)
            #print hierarchy[0]
            
        print "FRAME"
        cv2.imshow("Contour",frame)
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
