import cv2
import numpy as np

mitad1 = cv2.imread("./resources/m2_mitad1.png")
mitad2 = cv2.imread("./resources/m2_mitad2.png")

lienzo = np.full((400, 400, 3), 255, dtype=np.uint8)

dx = 0
dy = 0

M_trans = np.float32([
    [1, 0, dx],
    [0, 1, dy]
])

mitad1_recta = cv2.warpAffine(
    mitad1,
    M_trans,
    (mitad1.shape[1], mitad1.shape[0])
)

h1, w1 = mitad1_recta.shape[:2]
lienzo[0:h1, 0:w1] = mitad1_recta
h2, w2 = mitad2.shape[:2]
centro = (w2 // 2, h2 // 2)

M_rot = cv2.getRotationMatrix2D(
    centro,
    180,
    1.0
)

mitad2_recta = cv2.warpAffine(
    mitad2,
    M_rot,
    (w2, h2)
)

lienzo[h1:h1+h2, 0:w2] = mitad2_recta

cv2.imwrite("m2_qr_reconstruido.png", lienzo)
cv2.imshow("QR Reconstruido", lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()