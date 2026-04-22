import cv2 as cv
import numpy as np


img = cv.imread('./resources/m1_oscura 1.png', cv.IMREAD_GRAYSCALE)

x,y = img.shape
img2 = np.zeros((x,y), np.uint8)

for i in range(x):
	for j in range(y):
		if (img[i,j]*50) > 255:
			img2[i,j] = 255
		if img[i,j]*50 < 0:
			img2[i,j] = 0
		else:
			img2[i,j] = img[i,j]*50

img3 = np.zeros((x,y), np.uint8)

for i in range(x):
	for j in range(y):
		if (img2[i,j]+20) > 255:
			img3[i,j] = 255
		if img2[i,j]+20 < 0:
			img3[i,j] = 0
		else:
			img3[i,j] = img2[i,j]+20
			
img4 = np.zeros((x,y), np.uint8)

for i in range(x):
	for j in range(y):
		if (img3[i,j]*50) > 255:
			img4[i,j] = 255
		if img3[i,j]*50 < 0:
			img4[i,j] = 0
		else:
			img4[i,j] = img3[i,j]*50			


cv.imshow('imagen original', img)
cv.imshow('imagen recuperada x50', img2)
cv.imshow('imagen recuperada x50+20', img3)
cv.imshow('imagen recuperada vector', img4)
cv.waitKey(0)
cv.destroyAllWindows()
