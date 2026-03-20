import cv2 as cv
import numpy as np

img=np.ones([400,600], np.uint8)
img[1,1]=0

img = cv.line(img, (50, 200), (300, 50), (255), 3)
img = cv.line(img, (300, 50), (550, 200), (255), 3)
img = cv.line(img, (550, 200), (300, 350), (255), 3)
img = cv.line(img, (300,350), (50, 200), (255), 3)

img = cv.line(img, (180, 180), (180, 230), (255), 3)
img = cv.line(img, (180, 230), (230, 260), (255), 3)
img = cv.line(img, (230, 260), (230, 210), (255), 3)
#img = cv.line(img, (180, 180), (230, 210), (255), 3)

img = cv.line(img, (420, 180), (420, 230), (255), 3)
img = cv.line(img, (420, 230), (370, 260), (255), 3)
img = cv.line(img, (370, 260), (370, 210), (255), 3)
#img = cv.line(img, (420, 180), (370, 210), (255), 3)

img = cv.line(img, (180, 180), (300, 110), (255), 3)
img = cv.line(img, (300, 110), (420, 180), (255), 3)

img = cv.line(img, (300, 121), (300, 220), (255), 3)
img = cv.line(img, (300, 220), (230, 260), (255), 3)
img = cv.line(img, (300, 170), (230, 210), (255), 3)
img = cv.line(img, (300, 220), (370, 260), (255), 3)
img = cv.line(img, (300, 170), (370, 210), (255), 3)

img = cv.line(img, (200, 180), (180, 180), (255), 3)
img = cv.line(img, (200, 180), (230, 210), (255), 3)
img = cv.line(img, (200, 180), (300, 121), (255), 3)
img = cv.line(img, (400, 180), (420, 180), (255), 3)
img = cv.line(img, (400, 180), (370, 210), (255), 3)
img = cv.line(img, (400, 180), (300, 121), (255), 3)

img = cv.line(img, (195, 240), (195, 205), (255), 3)
img = cv.line(img, (215, 250), (215, 219), (255), 3)
img = cv.line(img, (195, 205), (215, 219), (255), 3)

img = cv.line(img, (320, 200), (350, 217), (255), 3)
img = cv.line(img, (320, 218), (320, 200), (255), 3)
img = cv.line(img, (350, 235), (320, 218), (255), 3)
img = cv.line(img, (350, 235), (320, 200), (255), 3)
img = cv.line(img, (350, 235), (350, 217), (255), 3)

cv.imshow("imagen",img)
cv.waitKey(0)
cv.destroyAllWindows()
