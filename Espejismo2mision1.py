import cv2
import numpy as np

img = cv2.imread("./resources/m1_oscura.png", cv2.IMREAD_GRAYSCALE)

# ── MODO RAW ────────────────────────────────────────────────────────────────

img_int32 = img.astype(np.int32)
altura, ancho = img_int32.shape
resultado = np.zeros((altura, ancho), dtype=np.int32)

for y in range(altura):
    for x in range(ancho):
        resultado[y, x] = img_int32[y, x] * 50

m1_x50 = np.clip(resultado, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50.png", m1_x50)
print("Guardado: m1_recuperado_x50.png")

# ── SEGUNDA FASE (RAW) ──────────────────────────────────────────────────────

resultado_mas20 = np.zeros((altura, ancho), dtype=np.int32)

for y in range(altura):
    for x in range(ancho):
        resultado_mas20[y, x] = int(m1_x50[y, x]) + 20

m1_x50_mas20 = np.clip(resultado_mas20, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50_mas20.png", m1_x50_mas20)
print("Guardado: m1_recuperado_x50_mas20.png")

# ── MODO VECTORIZADO ───────────────────────────────────────────────

img_vec_int32 = img.astype(np.int32) * 50
m1_x50_vec = np.clip(img_vec_int32, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50_vec.png", m1_x50_vec)
print("Guardado: m1_recuperado_x50_vec.png")

m1_x50_mas20_vec = cv2.add(m1_x50_vec, np.full_like(m1_x50_vec, 20))
cv2.imwrite("m1_recuperado_x50_mas20_vec.png", m1_x50_mas20_vec)
print("Guardado: m1_recuperado_x50_mas20_vec.png")
