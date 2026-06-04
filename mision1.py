import cv2 as cv
import numpy as np

img = cv.imread('resources/vehiculo.png')

M = np.float32([[1, 0, 300], [0, 1, 200]])

alto, ancho = img.shape[:2]
img_trasladada = cv.warpAffine(img, M, (ancho, alto))
cv.imwrite('mision1_resultado.png', img_trasladada)

cv.imshow('Original', img)
cv.imshow('Trasladada', img_trasladada)
cv.waitKey(0)
cv.destroyAllWindows()
