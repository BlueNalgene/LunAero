import cv2
import numpy as np
import timeit

filename = 'test.jpg'

start_time = timeit.default_timer()
img = cv2.imread(filename)
elapsed1 = timeit.default_timer() - start_time

start_time = timeit.default_timer()
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
gray = np.float32(gray)
dst = cv2.cornerHarris(gray,2,3,0.04)
#result is dilated for marking the corners, not important
dst = cv2.dilate(dst,None)
# Threshold for an optimal value, it may vary depending on the image.
img[dst>0.01*dst.max()]=[0,0,255]
elapsed2 = timeit.default_timer() - start_time

cv2.imshow('dst',img)
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()
print ("load time",elapsed1,",","calc time",elapsed2)
