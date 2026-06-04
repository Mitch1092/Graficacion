import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("GLOG_minloglevel", "2")

import sys
import math
import glfw
import cv2
import numpy as np
import mediapipe as mp
from OpenGL.GL import *
from OpenGL.GLU import *

# ── MediaPipe Tasks API ──────────────────────────────────────
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "hand_landmarker.task")

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
]

# ── Estado 3D (lo que antes controlaba el ratón) ─────────────
angle_x, angle_y = 0.0, 0.0
zoom = -5.0
pan_x, pan_y = 0.0, 0.0

# Posiciones previas normalizadas para calcular delta
prev_right_index = None
prev_left_index = None


# ── Dibujo de la casa (igual que casa.py) ────────────────────
def draw_cube():
    """Base de la casa"""
    glBegin(GL_QUADS)
    # Frente
    glColor3f(0.8, 0.5, 0.2)
    glVertex3f(-1, 0, 1)
    glVertex3f(1, 0, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)

    # Atrás
    glColor3f(0.7, 0.4, 0.2)
    glVertex3f(-1, 0, -1)
    glVertex3f(1, 0, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(-1, 1, -1)

    # Izquierda
    glColor3f(0.6, 0.3, 0.1)
    glVertex3f(-1, 0, -1)
    glVertex3f(-1, 0, 1)
    glVertex3f(-1, 1, 1)
    glVertex3f(-1, 1, -1)

    # Derecha
    glColor3f(0.6, 0.3, 0.1)
    glVertex3f(1, 0, -1)
    glVertex3f(1, 0, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(1, 1, -1)

    # Arriba
    glColor3f(0.9, 0.5, 0.3)
    glVertex3f(-1, 1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)

    # Abajo
    glColor3f(0.5, 0.3, 0.1)
    glVertex3f(-1, 0, -1)
    glVertex3f(1, 0, -1)
    glVertex3f(1, 0, 1)
    glVertex3f(-1, 0, 1)
    glEnd()


def draw_roof():
    """Techo piramidal rojo"""
    glBegin(GL_TRIANGLES)
    glColor3f(0.9, 0.1, 0.1)

    # Frente
    glVertex3f(-1, 1, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(0, 2, 0)

    # Atrás
    glVertex3f(-1, 1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(0, 2, 0)

    # Izquierda
    glVertex3f(-1, 1, -1)
    glVertex3f(-1, 1, 1)
    glVertex3f(0, 2, 0)

    # Derecha
    glVertex3f(1, 1, -1)
    glVertex3f(1, 1, 1)
    glVertex3f(0, 2, 0)
    glEnd()


def draw_ground():
    """Piso / calle (igual que casas.py)"""
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)
    glVertex3f(-20, 0, 20)
    glVertex3f(20, 0, 20)
    glVertex3f(20, 0, -20)
    glVertex3f(-20, 0, -20)
    glEnd()


# ── Dibujar landmarks sobre el frame de OpenCV ──────────────
def draw_hand_overlay(frame, keypoints, pinch_dist):
    for pt in keypoints:
        cv2.circle(frame, pt, 4, (255, 0, 0), cv2.FILLED)
    for c in HAND_CONNECTIONS:
        cv2.line(frame, keypoints[c[0]], keypoints[c[1]], (0, 255, 0), 2)

    if len(keypoints) >= 21:
        thumb, index = keypoints[4], keypoints[8]
        cv2.line(frame, thumb, index, (0, 0, 255), 2)
        cv2.circle(frame, thumb, 8, (0, 0, 255), cv2.FILLED)
        cv2.circle(frame, index, 8, (0, 0, 255), cv2.FILLED)
        mid = ((thumb[0] + index[0]) // 2, (thumb[1] + index[1]) // 2)
        cv2.putText(frame, f"{int(pinch_dist)} px", mid,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)


# ── Procesar resultados de MediaPipe y actualizar estado 3D ──
def process_hands(results, w, h):
    global angle_x, angle_y, zoom, pan_x, pan_y
    global prev_right_index, prev_left_index

    if not results.hand_landmarks:
        prev_right_index = None
        prev_left_index = None
        return None

    all_keypoints = []

    for idx, hand_lm in enumerate(results.hand_landmarks):
        handedness = "Left"
        if results.handedness and idx < len(results.handedness):
            handedness = results.handedness[idx][0].category_name

        keypoints = [(int(lm.x * w), int(lm.y * h)) for lm in hand_lm]

        if len(keypoints) < 21:
            continue

        thumb_tip = keypoints[4]
        index_tip = keypoints[8]
        pinch = math.hypot(index_tip[0] - thumb_tip[0],
                           index_tip[1] - thumb_tip[1])

        norm_x = index_tip[0] / w
        norm_y = index_tip[1] / h

        if handedness == "Right":
            # Rotación con el movimiento del índice
            if prev_right_index is not None:
                dx = (norm_x - prev_right_index[0]) * 80
                dy = (norm_y - prev_right_index[1]) * 80
                angle_y += dx
                angle_x += dy
            # Zoom con la pinza
            zoom = -3.0 - (pinch / w) * 10.0
            zoom = max(-15.0, min(-3.0, zoom))
            prev_right_index = (norm_x, norm_y)
        else:
            # Traslación con mano izquierda
            if prev_left_index is not None:
                dx = (norm_x - prev_left_index[0]) * 3
                dy = (norm_y - prev_left_index[1]) * 3
                pan_x += dx
                pan_y -= dy
            prev_left_index = (norm_x, norm_y)

        all_keypoints.append((keypoints, pinch))

    return all_keypoints


# ── Main ─────────────────────────────────────────────────────
def main():
    if not os.path.exists(MODEL_PATH):
        print("=" * 60)
        print(f"ERROR: No se encontró '{MODEL_PATH}'")
        print("Descárgalo con:")
        print(f"  wget -P {os.path.dirname(MODEL_PATH)} "
              "https://storage.googleapis.com/mediapipe-models/"
              "hand_landmarker/hand_landmarker/float16/latest/"
              "hand_landmarker.task")
        print("=" * 60)
        sys.exit(1)

    # Inicializar GLFW
    if not glfw.init():
        print("No se pudo inicializar GLFW")
        sys.exit(1)

    width, height = 640, 480
    window = glfw.create_window(width, height,
                                "Casa 3D – Control con Manos", None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)
    glViewport(0, 0, width, height)

    # Configuración OpenGL (igual que casa.py)
    glClearColor(0.5, 0.8, 1.0, 1.0)  # Fondo azul cielo
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    # Configurar MediaPipe
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        glfw.terminate()
        sys.exit(1)

    with HandLandmarker.create_from_options(options) as landmarker:
        while not glfw.window_should_close(window):
            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
                break

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                                data=frame_rgb)
            results = landmarker.detect(mp_image)

            # Actualizar ángulos/zoom/pan con las manos
            hand_data = process_hands(results, w, h)

            # Dibujar landmarks en la ventana de OpenCV
            if hand_data:
                for keypoints, pinch in hand_data:
                    draw_hand_overlay(frame, keypoints, pinch)

            info = ["Mano der: rotar", "Pinza der: zoom",
                    "Mano izq: mover", "ESC: salir"]
            for i, txt in enumerate(info):
                cv2.putText(frame, txt, (10, 22 + i * 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.imshow("MediaPipe - Camara", frame)
            cv2.waitKey(1)

            # ── Renderizar escena 3D (casa.py con gluLookAt) ──
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            cam_dist = -zoom
            gluLookAt(cam_dist * 0.6 + pan_x, cam_dist * 0.4 + pan_y, cam_dist,
                      pan_x, 1 + pan_y, 0,
                      0, 1, 0)

            glRotatef(angle_x, 1, 0, 0)
            glRotatef(angle_y, 0, 1, 0)

            draw_ground()
            draw_cube()
            draw_roof()

            glfw.swap_buffers(window)
            glfw.poll_events()

    cap.release()
    cv2.destroyAllWindows()
    glfw.terminate()


if __name__ == "__main__":
    main()



