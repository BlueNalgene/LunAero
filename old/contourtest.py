import cv2
import timeit

# Read image
start_time = timeit.default_timer()
src = cv2.imread("test.jpg", cv2.CV_LOAD_IMAGE_GRAYSCALE)
elapsed1 = timeit.default_timer() - start_time

# Set threshold and maxValue
start_time = timeit.default_timer()
thresh = 127
maxValue = 255

# Basic threshold example
th, dst = cv2.threshold(src, thresh, maxValue, cv2.THRESH_BINARY);

# Find Contours 
countours,hierarchy=cv2.findContours(dst,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

# Draw Contour
cv2.drawContours(dst,countours,-1,(255,255,255),3)
elapsed2 = timeit.default_timer() - start_time

cv2.imshow("Contour",dst)
cv2.waitKey(0)
print ("load image",elapsed1,",","calculate",elapsed2)
