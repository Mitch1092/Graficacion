import cv2 as cv
import numpy as np

img = cv.imread('./resources/examen/m1_oscura.png', 0)

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

cv.imshow('img', img)
cv.imshow('img2', img2)
cv.waitKey(0)
cv.destroyAllWindows()

