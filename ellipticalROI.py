#For OpenCV version 2.4.9
#OpenCV breaks when installed from pip on Ubuntu, so version is dependent on apt
#I had issues with cv2.cv.CV_HOUGH_GRADIENT

import cv2
import numpy as np

img = cv2.imread('current.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

ret,thresh = cv2.threshold(gray,40,255,0)
_,contours,hierarchy = cv2.findContours(thresh, 1, 2)

cnt = contours[0]

# We only care about the BIGGEST contour here
c = max(contours, key = cv2.contourArea)

ellipse = cv2.fitEllipse(c)
cv2.ellipse(img,ellipse,(0,255,0),2)

# These lines are just output checks for the ellipse, they can be omitted later.
print(str('FRAME')+str(ellipse[0][0])+','+str(ellipse[0][1])+','+str(ellipse[1][0])+','+str(ellipse[1][1])+','+str(ellipse[2]))
print(cv2.contourArea(c))

#if hierarchy[0][i][3] == (-1):
    #(x,y),radius = cv2.minEnclosingCircle(cnt)
    #center = (int(x),int(y))
    #radius = int(radius)
    #cv2.circle(img,center,radius,(0,255,0),2)
#if hierarchy[0][i][3] == 0:
    #(x,y),radius = cv2.minEnclosingCircle(cnt)
    #center = (int(x),int(y))
    #radius = int(radius)
    #cv2.circle(img,center,radius,(255,255,0),2)   
#i = 1 + i
    
#e = cv2.ellipse(gray,((1069.48254395,585.333190918),(815.770202637,835.336),149),66)
#e = cv2.ellipse(gray,(1069,585),(815,835),150,0,360,66,-1,8)
#e = cv2.ellipse2Poly((1069,585),(815,835),150,0,360,1)
#print e

# This makes an 'image' of all nothing with the same size as the original
mask = np.zeros(img.shape, dtype=np.uint8)
# This draws the ellipse onto the empty shape we just made.
# The parameters are from the fitEllipse, but they have to be INT.
cv2.ellipse(mask,(int(ellipse[0][0]),int(ellipse[0][1])),(int(ellipse[1][0]),int(ellipse[1][1])),int(ellipse[2]),0,360,(255, 255, 255),-1,8)
result = img & mask

# Now the mask is shifted such that the center of the ellipse is in the center of the screen.
rows,cols,_ = img.shape
xdi = (cols / 2) - int(ellipse[0][0])
ydi = (rows / 2) - int(ellipse[0][1])
M = np.float32([[1,0,xdi],[0,1,ydi]])
result = cv2.warpAffine(result, M, (cols,rows))

cv2.imshow('circles',result)
#print(str(pixlen))
cv2.waitKey(0)
cv2.destroyAllWindows()


