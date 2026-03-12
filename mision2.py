import cv2 as cv
import numpy as np
import math

mitad1 = cv.imread('./resources/examen/m2_mitad1.png',0)
mitad2 = cv.imread('./resources/examen/m2_mitad2.png',0)

img=np.ones([400,400], np.uint8)

x, y = mitad2.shape
rotated=np.ones([x,y], np.uint8)

for i in range(200):
	for j in range(400):	
		rotated[i,j] = mitad2[199-i,399-j]

for i in range(200):
	for j in range(400):	
		img[i,j] = mitad1[i,j]           
            
            			

for i in range(200):
	for j in range(400):	
		img[i+200,j] = rotated[i,j]


#cv.imshow('rotated', rotated)
cv.imshow('img', img)
#cv.imshow('mitad1', mitad1)
#cv.imshow('mitad2', mitad2)
cv.waitKey(0)
cv.destroyAllWindows()
