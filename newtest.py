#For OpenCV version 2.4.9
#OpenCV breaks when installed from pip on Ubuntu, so version is dependent on apt
#I had issues with cv2.cv.CV_HOUGH_GRADIENT

import cv2
import numpy as np

img = cv2.imread('current.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

ret,thresh = cv2.threshold(gray,127,255,0)
_,contours,hierarchy = cv2.findContours(thresh, 3, 2)

cnt = contours[0]
i = 0
       
for cnt in contours:
    if hierarchy[0][i][3] == (-1):
        (x,y),radius = cv2.minEnclosingCircle(cnt)
        center = (int(x),int(y))
        radius = int(radius)
        cv2.circle(img,center,radius,(0,255,0),2)
    if hierarchy[0][i][3] == 0:
        (x,y),radius = cv2.minEnclosingCircle(cnt)
        center = (int(x),int(y))
        radius = int(radius)
        cv2.circle(img,center,radius,(255,255,0),2)   
    i = 1 + i
    
col = gray[0]
row = gray
#e = cv2.ellipse(gray,((1069.48254395,585.333190918),(815.770202637,835.336),149),66)
e = cv2.ellipse(gray,((1069,585),(815,835),150),66)
#e = cv2.ellipse2Poly((1069,585),(815,835),150,0,360,1)
#print np.array(e).astype(np.float32)
#retin = cv2.pointPolygonTest(e,(gray[0][0]),0)
#print(retin)
for x, y in [(x,y) for x in row for y in col]:
    for z in x:
        cord = (z,y)
        if cord == (0,0):
            pass
        else:
            print cord
            # OK, so the pointPolygonTest function needs to have a tuple of floats to work (using Point2f format)
            # That specifically means it needs some (x,y) coordinates.
            hat = cv2.pointPolygonTest(np.array(e).astype(np.float32),cord,0)

    #if y > 0:
        
        #print(y)
    col -= 1


cv2.imshow('circles',gray)
#print(str(pixlen))
cv2.waitKey(0)
cv2.destroyAllWindows()


