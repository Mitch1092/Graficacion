import cv2
import numpy as np
import math

img = np.zeros((600, 600, 3), dtype=np.uint8)
img[:] = (40, 20, 20)
cv2.circle(img, (300, 300), 170, (0, 255, 255), 3)
cv2.circle(img, (300, 300), 110, (0, 255, 255), 2)
cv2.rectangle(img, (250, 260), (350, 340), (0, 0, 255), -1)
cv2.line(img, (0, 0), (599, 599), (255, 255, 255), 2)
cv2.line(img, (599, 0), (0, 599), (255, 255, 255), 2)
cx, cy = 300, 300
distancia = 140

for i in range(8):
    angulo = math.radians(i * 45)
    x = int(cx + distancia * math.cos(angulo))
    y = int(cy + distancia * math.sin(angulo))
    cv2.circle(img, (x, y), 8, (0, 255, 0), -1)

texto = "SECTOR-9"
fuente = cv2.FONT_HERSHEY_SIMPLEX
escala = 1.0
grosor = 2
(ancho_txt, alto_txt), _ = cv2.getTextSize(texto, fuente, escala, grosor)
x_txt = (600 - ancho_txt) // 2
y_txt = 560
cv2.putText(img, texto, (x_txt, y_txt), fuente, escala, (255, 255, 255), grosor)

cv2.imwrite("m3_sello_forjado_v2.png", img)
print("Imagen guardada como m3_sello_forjado_v2.png")
