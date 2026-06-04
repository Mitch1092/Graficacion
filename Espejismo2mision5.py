import cv2
import numpy as np

RUTA_TRICOLOR = "./m5_tricolor.png"
RUTA_MENSAJE  = "./m5_mensaje.png"

MENSAJE       = "Mensaje oculto xd"   
ALTO, ANCHO   = 300, 700          
COLOR_TEXTO   = (0, 10, 150)


def generar_tricolor():
    ruido = np.random.randint(50, 200, (ALTO, ANCHO, 3), dtype=np.uint8)
    fuente  = cv2.FONT_HERSHEY_DUPLEX
    escala  = 1.4
    grosor  = 2
    (tw, th), baseline = cv2.getTextSize(MENSAJE, fuente, escala, grosor)
    x = (ANCHO - tw) // 2
    y = (ALTO  + th) // 2

    cv2.putText(ruido, MENSAJE, (x, y), fuente, escala, COLOR_TEXTO, grosor, cv2.LINE_AA)

    cv2.imwrite(RUTA_TRICOLOR, ruido)
    print(f"Imagen guardada como {RUTA_TRICOLOR}")
    return ruido

def recuperar_mensaje(img):
    b, g, r = cv2.split(img)
    diff_rg = np.clip(r.astype(np.int16) - g.astype(np.int16), 0, 255).astype(np.uint8)
    normalizado = cv2.normalize(diff_rg, None, 0, 255, cv2.NORM_MINMAX)
    _, umbralizado = cv2.threshold(normalizado, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cv2.imwrite(RUTA_MENSAJE, umbralizado)
    print(f"Mensaje recuperado guardado como {RUTA_MENSAJE}")

if __name__ == "__main__":
    img = generar_tricolor()
    recuperar_mensaje(img)
