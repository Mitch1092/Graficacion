import cv2 as cv
import numpy as np

img2 = np.ones((400,400), np.uint8)*150

img = cv.imread('./resources/Dorohedoro.jpg',0)
print(img.shape)
cv.imshow('img', img)
cv.imshow('img2', img2)
cv.waitKey(0)
cv.destroyAllWindows()

