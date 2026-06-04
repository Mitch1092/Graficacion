import cv2
import numpy as np

# --- ACTIVIDAD 1: Cargar la imagen y aplicar la máscara para el color verde ---
img = cv2.imread('./resources/frutas.png')

if img is None:
    print("Error: No se pudo cargar la imagen './resources/frutas.png'")
    exit()

hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Rango para el color verde en HSV
# Hue para verde va aproximadamente de 40 a 85
lower_green = np.array([40, 100, 100])
upper_green = np.array([85, 255, 255])
mask_verde = cv2.inRange(hsv_img, lower_green, upper_green)


# --- ACTIVIDAD 2: Limpieza de la máscara (Apertura y Cierre) ---
kernel = np.ones((5,5), np.uint8)

# Apertura para eliminar pequeños ruidos de fondo
mask_apertura = cv2.morphologyEx(mask_verde, cv2.MORPH_OPEN, kernel)

# Cierre para rellenar huecos dentro de las frutas verdes detectadas
mask_limpia = cv2.morphologyEx(mask_apertura, cv2.MORPH_CLOSE, kernel)


# --- ACTIVIDAD 3: Conteo y cálculo de áreas ---
contornos, _ = cv2.findContours(mask_limpia, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

frutas_verdes_detectadas = 0
area_minima = 500  # Umbral para descartar basuras/ruidos

print("--- Análisis de Frutas Verdes ---")
for contorno in contornos:
    area = cv2.contourArea(contorno)
    
    if area > area_minima:
        frutas_verdes_detectadas += 1
        print(f"Fruta verde #{frutas_verdes_detectadas}: Área aproximada = {area} píxeles")
        
        # Dibujar el contorno en verde (0, 255, 0 en BGR)
        cv2.drawContours(img, [contorno], -1, (0, 255, 0), 3)

print("-" * 37)
print(f"Número total de frutas verdes detectadas: {frutas_verdes_detectadas}")


# --- Guardar todas las capturas generadas en el proceso ---
cv2.imwrite('verde_1_hsv.png', hsv_img)
cv2.imwrite('verde_2_mascara_sucia.png', mask_verde)
cv2.imwrite('verde_3_mascara_limpia.png', mask_limpia)
cv2.imwrite('verde_4_resultado_final.png', img)

print("Imágenes guardadas exitosamente para documentar el proceso del color verde.")
