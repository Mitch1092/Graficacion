import cv2
import numpy as np

# Cargar la máscara limpia generada en la actividad anterior
mask = cv2.imread('frutas_mascara_limpia.png', cv2.IMREAD_GRAYSCALE)

contornos, jerarquia = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

frutas_detectadas = 0
area_minima = 500  # Umbral para descartar ruidos pequeños que hayan sobrevivido

print("--- Análisis de Regiones (Frutas) ---")

for contorno in contornos:
    # Calcular el área del contorno actual
    area = cv2.contourArea(contorno)
    
    if area > area_minima:
        frutas_detectadas += 1
        print(f"Fruta válida #{frutas_detectadas}: Área aproximada = {area} píxeles")

print("-" * 37)
print(f"Número total de frutas detectadas: {frutas_detectadas}")

