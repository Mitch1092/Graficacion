import cv2 as cv
import numpy as np

img = cv.imread('resources/m4_ruido.png')
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

bajo = np.array([80, 100, 100])
alto = np.array([100, 255, 255])
mascara = cv.inRange(hsv, bajo, alto)

cv.imshow('Original', img)
cv.imshow('Mascara', mascara)
cv.waitKey(0)
cv.destroyAllWindows()
