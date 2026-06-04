import cv2 as cv
import numpy as np

img=np.ones([400,400], np.uint8)*255

i=j=0
for i in range(200):
	for j in range(200):
		img[i,j]=255-i

cv.imshow("imagen",img)
cv.waitKey(0)
cv.destroyAllWindows()
