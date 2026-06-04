import cv2
import numpy as np

img = cv2.imread('./resources/frutas.png')

if img is None:
    print("Error: No se pudo cargar la imagen")
    exit()

hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
mask1 = cv2.inRange(hsv_img, lower_red1, upper_red1)

lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([180, 255, 255])
mask2 = cv2.inRange(hsv_img, lower_red2, upper_red2)

mask = cv2.bitwise_or(mask1, mask2)

cv2.imwrite('frutas_original.png', img)
cv2.imwrite('frutas_hsv.png', hsv_img)
cv2.imwrite('frutas_mascara.png', mask)

