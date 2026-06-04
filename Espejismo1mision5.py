import cv2 as cv
import numpy as np
import math

lienzo = np.zeros((500, 500, 3), dtype=np.uint8)

t = 0.0
while t <= 2 * math.pi:
    x = int(250 + 150 * math.sin(3 * t))
    y = int(250 + 150 * math.sin(2 * t))
    cv.circle(lienzo, (x, y), 2, (255, 255, 255), -1)
    t += 0.01

cv.imshow("Lissajous", lienzo)
cv.waitKey(0)
cv.destroyAllWindows()
