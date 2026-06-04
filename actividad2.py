import cv2
import numpy as np

img = cv2.imread('./resources/frutas.png')

hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
mask1 = cv2.inRange(hsv_img, lower_red1, upper_red1)

lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([180, 255, 255])
mask2 = cv2.inRange(hsv_img, lower_red2, upper_red2)

mask_original = cv2.bitwise_or(mask1, mask2)
kernel = np.ones((5,5), np.uint8)
mask_apertura = cv2.morphologyEx(mask_original, cv2.MORPH_OPEN, kernel)
mask_limpia = cv2.morphologyEx(mask_apertura, cv2.MORPH_CLOSE, kernel)

cv2.imwrite('frutas_mascara_sin_limpiar.png', mask_original)
cv2.imwrite('frutas_mascara_limpia.png', mask_limpia)

