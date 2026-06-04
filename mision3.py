import cv2
import numpy as np

img_microfilm = cv2.imread('./resources/microfilm.png')

# Método OpenCV:
recorte = img_microfilm[900:1100, 900:1100]
recorte_ampliado = cv2.resize(recorte, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)


# Método RAW:
lienzo_raw = np.zeros((1000, 1000, 3), dtype=np.uint8)
Sx = 5
Sy = 5

alto, ancho = recorte.shape[:2]

for y in range(alto):
    for x in range(ancho):
        Ynuevo = y * Sy
        Xnuevo = x * Sx
        lienzo_raw[Ynuevo:Ynuevo+Sy, Xnuevo:Xnuevo+Sx] = recorte[y, x]

cv2.imshow('Recorte Ampliado RAW', lienzo_raw)
cv2.imshow('Recorte Ampliado OpenCV', recorte_ampliado)
cv2.waitKey(0)
cv2.destroyAllWindows()
