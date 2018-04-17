import numpy as np
import cv2

frame = cv2.imread('migrant_snap.png')
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
_, contours, hierarchy = cv2.findContours(thresh, 2, 1)
if contours:
	ellipse = max(contours, key=cv2.contourArea)
	ellipse = cv2.fitEllipse(ellipse)
	mask = np.zeros(frame.shape, dtype=np.uint8)
	#cv2.ellipse(mask, (int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]/2), int(ellipse[1][1]/2)), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
	#print ellipse
	cv2.ellipse(mask, (int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]/2), int(ellipse[1][1]/2)), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
	result = frame & mask
	cv2.ellipse(mask, (int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]/2.2), int(ellipse[1][1]/2.2)), int(ellipse[2]), 0, 360, (0, 0, 0), -1, 8)
	mask = np.invert(mask)
	result = ~~(result & mask)

cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.resizeWindow("frame", 700, 500)
cv2.imshow("frame", frame)
cv2.namedWindow("gray", cv2.WINDOW_NORMAL)
cv2.resizeWindow("gray", 700, 500)
cv2.imshow("gray", gray)
#cv2.namedWindow("ellipse", cv2.WINDOW_NORMAL)
#cv2.resizeWindow("ellipse", 700, 500)
#cv2.imshow("ellipse", ellipse)
cv2.namedWindow("mask", cv2.WINDOW_NORMAL)
cv2.resizeWindow("mask", 700, 500)
cv2.imshow("mask", mask)
cv2.namedWindow("result", cv2.WINDOW_NORMAL)
cv2.resizeWindow("result", 700, 500)
cv2.imshow("result", result)

if cv2.waitKey(0) & 0xFF == ord('q'):
	cv2.destroyAllWindows()









		##ellipse = max(contours, key=cv2.contourArea)
		##ellipse = cv2.fitEllipse(ellipse)
		#mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
		#cv2.ellipse(mask, (0, 0), (int(ellipse[1][0]/2.5), \
						#int(ellipse[1][1]/2.5)), int(ellipse[2]), 0, 360, (0, 0, 0), -1, 8)
		##mask = np.invert(mask)
		#resulttwo = ~~(result & mask)
		#cv2.namedWindow("mask", cv2.WINDOW_NORMAL)
		#cv2.resizeWindow("mask", 700, 500)
		#cv2.imshow("mask", mask)
