import cv2 as cv

img = cv.imread('./resources/Negative.jpg')
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
cv.imshow('hsv', hsv)
cv.imshow('img', img)
cv.waitKey(0)
cv.destroyAllWindows()
