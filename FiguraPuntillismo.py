import cv2 as cv
import numpy as np

img=np.ones([100,100], np.uint8)
img[1,1]=0

i=j=0
for i in range(100):
	for j in range(100):
		if i+j<50 or i+j>150:
			img[i,j]=255
		if j>50 and i<50 and j-i>50:
			img[i,j]=255
		if i>50 and j<50 and i-j>50:
			img[i,j]=255
		
			
for i in range(100):
	for j in range(100):
		if j==33 or j==66:
			if i>30 and i<50:
				img[i,j]=150
		if i==60:
			if j>33 and j<66:
				img[i,j]=150
		if j==50 or j==60 or j==40:
			if i>60 and i<75:
				img[i,j]=150
		if i==75:
			if j>40 and j<60:
				img[i,j]=150						
				


cv.imshow("imagen",img)
cv.waitKey(0)
cv.destroyAllWindows()
