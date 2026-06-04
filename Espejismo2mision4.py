import cv2
import numpy as np

img = cv2.imread("./resources/m4_ruido.png")

kernel = np.ones((3, 3), dtype=np.float32) / 9.0
suavizada = cv2.filter2D(img, -1, kernel)
cv2.imwrite("m4_suavizada.png", suavizada)
print("Imagen guardada como m4_suavizada.png")

hsv = cv2.cvtColor(suavizada, cv2.COLOR_BGR2HSV)
low_cyan  = np.array([ 85, 100,  50], dtype=np.uint8)
high_cyan = np.array([100, 255, 255], dtype=np.uint8)
mask_cyan = cv2.inRange(hsv, low_cyan, high_cyan)

cv2.imwrite("m4_mask_cyan.png", mask_cyan)
print("Máscara guardada como m4_mask_cyan.png")
