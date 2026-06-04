
### [`mision1.py`]
**Traslación de imagen con OpenCV**

Carga la imagen `resources/vehiculo.png` y le aplica una **traslación 2D**: desplaza la imagen **300 píxeles a la derecha** y **200 píxeles hacia abajo** usando una matriz de transformación afín (`np.float32`) con `cv2.warpAffine`. Muestra la imagen original y la trasladada en ventanas separadas, y guarda el resultado en `mision1_resultado.png`.

---

### [`mision2.py`]
**Rotación de imagen (código QR) con OpenCV**

Carga `resources/qr_rotado.png` (un código QR que llega rotado) y aplica una **rotación de 315°** alrededor del punto central `(250, 250)` usando `cv2.getRotationMatrix2D` y `cv2.warpAffine`. El objetivo es enderezar el QR para dejarlo legible, y el resultado se muestra en pantalla.

---

### [`mision3.py`]
**Escalado de imagen por dos métodos**

Carga `resources/microfilm.png`, **recorta una región de 200×200 px** en las coordenadas `[900:1100, 900:1100]`, y luego amplia ese recorte ×5 de **dos maneras distintas**:
- **Método OpenCV**: usa `cv2.resize` con interpolación cúbica (`INTER_CUBIC`).
- **Método RAW (manual)**: implementa el escalado a mano con un doble `for`, replicando cada píxel en un bloque de 5×5 en un lienzo negro de 1000×1000.

Muestra ambas versiones en paralelo para comparar la calidad del resultado.

---