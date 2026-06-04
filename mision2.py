import cv2
import numpy as np

img_qr = cv2.imread('./resources/qr_rotado.png')

centro = (250, 250)
angulo = 315
escala = 1.0

matriz_rotacion = cv2.getRotationMatrix2D(centro, angulo, escala)
dimensiones = (img_qr.shape[1], img_qr.shape[0])
img_resultado = cv2.warpAffine(img_qr, matriz_rotacion, dimensiones)

cv2.imshow('QR Rotado', img_resultado)
cv2.waitKey(0)
cv2.destroyAllWindows()
