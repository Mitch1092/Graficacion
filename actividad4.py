import cv2
import numpy as np

# --- ACTIVIDAD 1: Cargar la imagen y aplicar la máscara para el color amarillo ---
img = cv2.imread('./resources/frutas.png')

if img is None:
    print("Error: No se pudo cargar la imagen './resources/frutas.png'")
    exit()

hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Rango para el color amarillo en HSV
# Aumentamos el Hue mínimo y bajamos el máximo para evitar naranjas y verdes
# Aumentamos la saturación y el valor mínimos para evitar tonos cafés o sombras
lower_yellow = np.array([22, 130, 130])
upper_yellow = np.array([35, 255, 255])
mask_amarilla = cv2.inRange(hsv_img, lower_yellow, upper_yellow)


# --- ACTIVIDAD 2: Limpieza de la máscara (Apertura y Cierre) ---
kernel = np.ones((5,5), np.uint8)

# Apertura para eliminar pequeños ruidos de fondo
mask_apertura = cv2.morphologyEx(mask_amarilla, cv2.MORPH_OPEN, kernel)

# Cierre para rellenar huecos dentro de las frutas amarillas detectadas
mask_limpia = cv2.morphologyEx(mask_apertura, cv2.MORPH_CLOSE, kernel)


# --- ACTIVIDAD 3: Conteo y cálculo de áreas ---
contornos, _ = cv2.findContours(mask_limpia, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

frutas_amarillas_detectadas = 0
area_minima = 500  # Umbral para descartar basuras/ruidos

print("--- Análisis de Frutas Amarillas ---")
for contorno in contornos:
    area = cv2.contourArea(contorno)
    
    if area > area_minima:
        frutas_amarillas_detectadas += 1
        print(f"Fruta amarilla #{frutas_amarillas_detectadas}: Área aproximada = {area} píxeles")
        
        # Dibujar el contorno en amarillo (0, 255, 255 en BGR)
        cv2.drawContours(img, [contorno], -1, (0, 255, 255), 3)

print("-" * 37)
print(f"Número total de frutas amarillas detectadas: {frutas_amarillas_detectadas}")


# --- Guardar todas las capturas generadas en el proceso ---
cv2.imwrite('amarillo_1_hsv.png', hsv_img)
cv2.imwrite('amarillo_2_mascara_sucia.png', mask_amarilla)
cv2.imwrite('amarillo_3_mascara_limpia.png', mask_limpia)
cv2.imwrite('amarillo_4_resultado_final.png', img)

print("Imágenes guardadas exitosamente para documentar el proceso del color amarillo.")



