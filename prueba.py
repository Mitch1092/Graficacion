import cv2 as cv

img = cv.imread('./resources/Dorohedoro.jpg')
cv.imshow('img', img)
cv.waitKey(0)
cv.destroyAllWindows()
