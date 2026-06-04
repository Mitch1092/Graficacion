import cv2 as cv
import numpy as np

img = np.zeros((500, 500, 3), dtype=np.uint8)
img[:] = (50, 20, 20)

cv.circle(img, (250, 250), 100, (0, 255, 255), 3)

cv.rectangle(img, (200, 200), (300, 300), (0, 0, 255), -1)

cv.line(img, (0, 0), (500, 500), (255, 255, 255), 2)
cv.line(img, (500, 0), (0, 500), (255, 255, 255), 2)

cv.imwrite('m3_sello_forjado.png', img)
