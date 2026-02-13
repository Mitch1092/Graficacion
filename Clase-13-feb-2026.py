import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)
ret, img = cap.read()
x,y,z = img.shape
fondo = np.zeros((x,y), np.uint8)
cv.imshow('fondo',fondo)

while True:
	ret, img = cap.read()
	if ret:
		r,g,b=cv.split(img)
		mr=cv.merge([fondo,fondo,r])
		mg=cv.merge([fondo,g,fondo])
		mb=cv.merge([b,fondo,fondo])
		cv.imshow('videor',mr)
		cv.imshow('videog',mg)
		cv.imshow('videob',mb)
		cv.imshow('Video', img)
	else:
		print('No me pude conectar a la camara')	
	k = cv.waitKey(1)
	if k==27:
		break
cap.release()
cv.destroyAllWindows()		
