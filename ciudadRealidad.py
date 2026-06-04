from OpenGL.raw.GL.VERSION.GL_1_0 import glPopMatrix
from OpenGL.raw.GL.VERSION.GL_1_0 import glPushMatrix
import glfw
import cv2
import mediapipe as mp
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import keyboard as key 
import random

# ============================================================
# Configuración del Entorno y MediaPipe
# ============================================================

# Inicializar MediaPipe Hands para la captura de Landmarks
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Dimensiones y Título de la Ventana GLFW
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_TITLE = "Ciudad Futurista 3D con Sombras Proyectadas y Landmarks"

# Variables globales para control de cámara (gluLookAt)
moverx, movery, moverz,dx,dz,girar = 0, 0,0,0,0,0

# Color de fondo (cielo futurista oscuro / modo noche elegante)
r, g, b = 0.04, 0.04, 0.08

t = glfw.get_time()

# Posición de la luz principal (fuente del sombreado)
POS_LUZ = (4.0, 10.0, 2.0)

def init_glfw():
    """Inicializa GLFW y crea una ventana OpenGL compatible con el fixed-function pipeline."""
    if not glfw.init():
        raise Exception("No se pudo inicializar GLFW")
    
    # Obtener el monitor primario para pantalla completa
    monitor = glfw.get_primary_monitor()
    if monitor:
        mode = glfw.get_video_mode(monitor)
        window = glfw.create_window(mode.size.width, mode.size.height, WINDOW_TITLE, monitor, None)
    else:
        window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)
        
    if not window:
        glfw.terminate()
        raise Exception("No se pudo crear la ventana GLFW")
    
    glfw.make_context_current(window)
    glfw.swap_interval(1) # Habilitar sincronización vertical (VSync)
    return window

# ============================================================
# Configuración Inicial de OpenGL
# ============================================================
def setup_opengl():
    """Establece los parámetros iniciales de renderizado de OpenGL."""
    glClearColor(r, g, b, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    
    # Habilitar Blending para soportar transparencia/cúpulas de cristal
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Suavizado de líneas
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

def create_video_texture():
    """Genera un identificador de textura en 2D para el feed de la cámara web."""
    video_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, video_tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return video_tex

def setup_lights():
    """Configura la iluminación del mundo futurista."""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)  # Luz de relleno
    glEnable(GL_COLOR_MATERIAL)
    
    # El material responderá tanto a la iluminación difusa como a la ambiental
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Luz principal (Luz direccional/puntual que determina las sombras)
    glLightfv(GL_LIGHT0, GL_POSITION, (POS_LUZ[0], POS_LUZ[1], POS_LUZ[2], 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 0.98, 0.9, 1.0))  
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.25, 0.25, 0.35, 1.0)) 
    
    # Luz de relleno lateral 
    glLightfv(GL_LIGHT1, GL_POSITION, (-6.0, 4.0, -4.0, 0.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.3, 0.4, 0.6, 1.0))

# Funciones de Dibujo

def normal_tri(v1, v2, v3, normal_defecto=(0.0, 1.0, 0.0)):
    """Calcula matemáticamente la normal unitaria de un polígono triangular."""
    ux = v2[0] - v1[0]
    uy = v2[1] - v1[1]
    uz = v2[2] - v1[2]

    vx = v3[0] - v1[0]
    vy = v3[1] - v1[1]
    vz = v3[2] - v1[2]

    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx

    longitud = math.sqrt(nx*nx + ny*ny + nz*nz)
    if longitud < 1e-8:
        return normal_defecto

    return (nx/longitud, ny/longitud, nz/longitud)

def plataforma_plana(lado1, lado2,altura, color=(1.0, 1.0, 1.0)):
    """Dibuja una plataforma base o plano rectangular."""
    glBegin(GL_QUADS)
    glColor3f(*color)
    glNormal3f(0.0, 1.0, 0.0) 
    
    glVertex3f(-lado1, altura, lado2)
    glVertex3f(lado1, altura, lado2)
    glVertex3f(lado1, altura, -lado2)
    glVertex3f(-lado1, altura, -lado2)
    glEnd()

def anillo_elipsoide(a1, b1, a2, b2, angulo_limite, capa, color=(1.0, 1.0, 1.0)):
    """Genera una elipse o anillo circular en el plano XZ usando un strip de quads."""
    glPushMatrix()
    glTranslatef(0.0, capa, 0.0)
    glBegin(GL_QUAD_STRIP)
    glColor3f(*color)
    glNormal3f(0.0, 1.0, 0.0)

    for i in range(int(angulo_limite) + 1): 
        ang = math.radians(i)
        x1 = a1 * math.cos(ang)
        z1 = b1 * math.sin(ang)
        x2 = a2 * math.cos(ang)
        z2 = b2 * math.sin(ang)

        glVertex3f(x1, 0.0, z1)
        glVertex3f(x2, 0.0, z2)

    glEnd()
    glPopMatrix()

def cubo(alto, ancho, largo, color_lados, color_arriba, color_abajo):
    """
    Construye un paralelepípedo de forma optimizada y diferente, aplicando
    las normales correctas en cada cara para que la iluminación sea realista.
    """
    w = ancho / 2.0
    l = largo / 2.0
    
    glBegin(GL_QUADS)
    
    # Cara frontal 
    glNormal3f(0.0, 0.0, 1.0)
    glColor3f(*color_lados)
    glVertex3f(-w, 0.0, l); glVertex3f(w, 0.0, l); glVertex3f(w, alto, l); glVertex3f(-w, alto, l)
    
    # Cara trasera 
    glNormal3f(0.0, 0.0, -1.0)
    glColor3f(*color_lados)
    glVertex3f(-w, 0.0, -l); glVertex3f(-w, alto, -l); glVertex3f(w, alto, -l); glVertex3f(w, 0.0, -l)

    # Cara izquierda 
    glNormal3f(-1.0, 0.0, 0.0)
    glColor3f(*color_lados)
    glVertex3f(-w, 0.0, -l); glVertex3f(-w, 0.0, l); glVertex3f(-w, alto, l); glVertex3f(-w, alto, -l)
    
    # Cara derecha 
    glNormal3f(1.0, 0.0, 0.0)
    glColor3f(*color_lados)
    glVertex3f(w, 0.0, -l); glVertex3f(w, alto, -l); glVertex3f(w, alto, l); glVertex3f(w, 0.0, l)
    
    # Cara superior
    glNormal3f(0.0, 1.0, 0.0)
    glColor3f(*color_arriba)
    glVertex3f(-w, alto, -l); glVertex3f(w, alto, -l); glVertex3f(w, alto, l); glVertex3f(-w, alto, l)
    
    # Cara inferior
    glNormal3f(0.0, -1.0, 0.0)
    glColor3f(*color_abajo)
    glVertex3f(-w, 0.0, -l); glVertex3f(-w, 0.0, l); glVertex3f(w, 0.0, l); glVertex3f(w, 0.0, -l)

    glEnd()

def piramide(alto, ancho, largo, altura_base, color):
    """
    Construye una pirámide basándose en un bucle iterativo que une
    los vértices de la base con la cima, recalculando normales exactas.
    """
    w = ancho / 2.0
    l = largo / 2.0
    cima_y = alto + altura_base
    cima = (0.0, cima_y, 0.0)

    vertices_base = [
        (-w, altura_base, l),
        (w, altura_base, l),
        (w, altura_base, -l),
        (-w, altura_base, -l)
    ]

    glBegin(GL_TRIANGLES)
    glColor3f(*color)
    for i in range(4):
        v1 = vertices_base[i]
        v2 = vertices_base[(i + 1) % 4]
        n = normal_tri(v1, v2, cima)
        glNormal3f(*n)
        glVertex3f(*v1)
        glVertex3f(*v2)
        glVertex3f(*cima)
    glEnd()

    # Tapa inferior de la pirámide
    glBegin(GL_QUADS)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-w, altura_base, -l)
    glVertex3f(-w, altura_base, l)
    glVertex3f(w, altura_base, l)
    glVertex3f(w, altura_base, -l)
    glEnd()

def esfera(radio, color=(1.0, 1.0, 1.0)):
    """Renderiza una esfera tridimensional estilizada."""
    if len(color) == 4:
        glColor4f(*color)
    else:
        glColor3f(*color)
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radio, 24, 24)
    gluDeleteQuadric(quad)

def linea_color(p1, p2, color=(1.0, 1.0, 1.0), grosor=2.0):
    """Dibuja un segmento de recta coloreado."""
    glDisable(GL_LIGHTING)
    glLineWidth(grosor)
    glColor3f(*color)
    glBegin(GL_LINES)
    glVertex3f(*p1)
    glVertex3f(*p2)
    glEnd()
    glEnable(GL_LIGHTING)

def tubo_cilindrico(ang_in, ang_fin, radio, largo, color=(1.0, 1.0, 1.0)):
    """Genera la pared exterior de un cilindro sin tapas."""
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(ang_in, ang_fin + 1):
        x1 = math.cos(math.radians(i))
        y1 = math.sin(math.radians(i))
        
        glColor3f(*color)
        glNormal3f(x1, y1, 0.0)
        glVertex3f(x1 * radio, y1 * radio, 0.0)
        glVertex3f(x1 * radio, y1 * radio, largo)
    glEnd()

def cilindro_solido(ang_in, ang_fin, radio, largo, color=(1.0, 1.0, 1.0)):
    """Crea un cilindro sólido con tapas en ambos extremos."""
    # Tubo principal
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(ang_in, ang_fin + 1):
        x1 = math.cos(math.radians(i))
        y1 = math.sin(math.radians(i))

        glColor3f(*color)
        glNormal3f(x1, y1, 0.0)
        glVertex3f(x1 * radio, y1 * radio, 0.0)
        glVertex3f(x1 * radio, y1 * radio, largo)
    glEnd()

    # Tapa inferior 
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(*color)
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(ang_in, ang_fin + 1):
        x1 = math.cos(math.radians(i)) * radio
        y1 = math.sin(math.radians(i)) * radio
        glVertex3f(x1, y1, 0.0)
    # Cerrar abanico
    x1 = math.cos(math.radians(ang_in)) * radio
    y1 = math.sin(math.radians(ang_in)) * radio
    glVertex3f(x1, y1, 0.0)
    glEnd()

    # Tapa superior 
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(*color)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, largo)
    for i in range(ang_fin, ang_in - 1, -1):
        x1 = math.cos(math.radians(i)) * radio
        y1 = math.sin(math.radians(i)) * radio
        glVertex3f(x1, y1, largo)
    # Cerrar abanico
    x1 = math.cos(math.radians(ang_fin)) * radio
    y1 = math.sin(math.radians(ang_fin)) * radio
    glVertex3f(x1, y1, largo)
    glEnd()


# Torres

def nube():
    COLOR_NUBE = (1.0, 0.75, 0.85)  # Rosa clarito
    a=-2
    b=-1
    for i in range(5):
        glPushMatrix()
        glTranslatef(a,0,0) 
        esfera(1, COLOR_NUBE)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(a,0,1)
        esfera(1, COLOR_NUBE)
        glPopMatrix()
        a+=1

        if(b<2):
            glPushMatrix()
            glTranslatef(b,1,0) 
            esfera(1, COLOR_NUBE)
            glPopMatrix()
            

            glPushMatrix()
            glTranslatef(b,1,1) 
            esfera(1, COLOR_NUBE)
            glPopMatrix()
            
            b+=1

def semaforo():
    t=glfw.get_time()
    distancia=math.sin(t*2)

    glPushMatrix()
    glTranslatef(0,distancia,0)
    #Color de las torres
    cubo(1,0.5,0.5,(0.4, 0.7, 0.95),(0.4, 0.7, 0.95),(0.4, 0.7, 0.95))

    glPushMatrix()
    glTranslatef(0,0.2,0.3)
    cubo(0.15,0.15,0.15,(1,0,0),(1,0,0),(1,0,0)) #color rojo
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0,0.5,0.3)
    cubo(0.15,0.15,0.15,(1,1,0),(1,1,0),(1,1,0)) #color amarillo
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0,0.8,0.3)
    cubo(0.15,0.15,0.15,(0,1,0),(0,1,0),(0,1,0)) #color verde
    glPopMatrix()


    oscilacion_llama = 1.0 + 0.7 * math.sin(t * 3.0)
    glPushMatrix()
    glTranslatef(0.0, -0.2, 0)
    glScalef(1.5, 1.5, oscilacion_llama)
    glRotatef(180.0, 1.0, 0.0, 0.0)
    piramide(0.35, 0.16, 0.16, 0.0, (1.0, 0.35, 0.0))
    glPopMatrix()

    glPopMatrix()
def monstruo():
    #def esfera(radio, color=(1.0, 1.0, 1.0)):
    t=glfw.get_time()
    a=1+(0.1*math.sin(t))
    b=1+(0.3*math.sin(t))
    c=1+(0.5*math.sin(t))
    #Primera parte
    for i in  range (8):
        glPushMatrix()
        glScalef(1*a,1*a,1*a)
        x=math.cos(math.radians(i*45))
        z=math.sin(math.radians(i*45))
        glTranslatef(x,0,z)
        esfera(0.8,(0,1,0))
        glPopMatrix()
    #segunda parte
    for i in  range (12):
        glPushMatrix()
        glScalef(1*b,1*b,1*b)
        x=math.cos(math.radians(i*35))
        z=math.sin(math.radians(i*35))
        glTranslatef(x,0.9,z)
        esfera(0.7,(0,1,0))
        glPopMatrix()
    #Tercera parte
    for i in  range (8):
        glPushMatrix()
        glScalef(1*c,1*c,1*c)
        x=math.cos(math.radians(i*60))
        z=math.sin(math.radians(i*60))
        glTranslatef(x,1.6,z)
        esfera(0.6,(0,1,0))
        glPopMatrix()
    #Cabeza
    glPushMatrix()
    glScalef(1*c,1*c,1*c)
    glTranslatef(0,2.2,0)
    esfera(0.8,(0,1,0))
    glPopMatrix()
    #Parte blanca del ojo
    glPushMatrix()
    glScalef(0.8*c,0.8*c,0.8*c)
    glTranslatef(0,2.2,1.5)
    esfera(0.8,(1,1,1))
    glPopMatrix()

    #Pupila del monstruo
    #que vayan de 0 a 180
    w=math.cos(t)*0.8
    f=math.sin(t)*0.8
    g=math.tan(t)*0.8
    glPushMatrix()
    glScalef(0.8*c,0.8*c,0.8*c)
    glTranslatef(w,f+2.2,g+1.5)
    esfera(0.1,(0,0,0))
    glPopMatrix()
    
    
def tuberia_toxica(x, y, z):
    #Tubo vertical que saca particulas verdes
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Tubo
    glPushMatrix()
    glRotatef(-90.0, 1.0, 0.0, 0.0) 
    cilindro_solido(0, 360, 0.3, 2.0, (0.1, 0.12, 0.1))
    glPopMatrix()

    # Burbujas tóxicas 
    t = glfw.get_time()
    for i in range(4): 
        desfase = i * 0.7 
        velocidad = 2.0
        altura_burbuja = ((t * velocidad + desfase) % 1.5) 
        
        if altura_burbuja > 0.1: 
            # Se encogen a medida que suben 
            escala = max(0.0, 1.0 - (altura_burbuja / 1.5)) 
            
            glPushMatrix()
            desp_x = math.sin(t * 3.0 + i * 10) * 0.15
            desp_z = math.cos(t * 2.0 + i * 5) * 0.15
            
            
            glTranslatef(desp_x, 2.0 + altura_burbuja, desp_z)
            esfera(0.12 * escala, (0.2, 1.0, 0.2))
            glPopMatrix()

    glPopMatrix() 

def dron_policial(x, y, z):
    #Dron flotando con hélices
    t = glfw.get_time()
    # Flote 
    flote_y = y + math.sin(t * 2.0) * 0.15 

    glPushMatrix()
    glTranslatef(x, flote_y, z)

    # Cuerpo 
    color_dron = (0.05, 0.05, 0.05)
    cubo(0.3, 0.8, 0.8, color_dron, (0.15, 0.15, 0.15), (0.0, 0.0, 0.0))

    # Luz
    glPushMatrix()
    glTranslatef(0.0, 0.15, 0.4) 
    esfera(0.08, (1.0, 0.0, 1.0))
    glPopMatrix()

    # Hélice 
    glPushMatrix()
    glTranslatef(0.0, 0.35, 0.0) 
    glRotatef(t * 1500.0, 0.0, 1.0, 0.0) 
    
    # Aspas 
    color_aspa = (0.5, 0.5, 0.5)
    cubo(0.02, 1.4, 0.1, color_aspa, color_aspa, color_aspa)
    cubo(0.02, 0.1, 1.4, color_aspa, color_aspa, color_aspa)
    glPopMatrix()

    glPopMatrix()



def camara_vigilancia_rotatoria(x, y, z):
    #Camara de seguridad girando de lado a lado con un tubo largo
    t = glfw.get_time()
    
    # Oscila de -60 a 60 grados
    velocidad_paneo = 1.0
    angulo_pan = math.sin(t * velocidad_paneo) * 60.0 

    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Poste
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, 0.05, 2.4, (0.25, 0.25, 0.28)) 
    glPopMatrix()
    
    
    # Cabeza de la cámara
    glPushMatrix()
    glTranslatef(0.0, 2.9, 0.0)
    
    # Paneo horizontal 
    glRotatef(angulo_pan, 0.0, 1.0, 0.0)
    
    # Inclinación hacia abajo
    glRotatef(55.0, 1.0, 0.0, 0.0) 

    # Cuerpo de la cámara f 
    color_metal = (0.15, 0.15, 0.15)
    cubo(0.4, 0.3, 0.6, color_metal, (0.2, 0.2, 0.2), (0.1, 0.1, 0.1))
    
    # Lente óptico 
    glPushMatrix()
    glTranslatef(0.0, 0.2, 0.3) 
    esfera(0.12, (1.0, 0.0, 0.0))
    glPopMatrix()

    glPopMatrix() # Fin de la cabeza rotatoria
    glPopMatrix() # Fin de la cámara completa

def infonavit_sin_puerta(color_pared=(1.0, 1.0, 1.0), color_ventana=(0.0, 0.0, 0.0), escala=1.0):
        #paredes
    cubo(3,4,4,color_pared,color_pared,color_pared)
    #ventanas
    glPushMatrix()
    glTranslatef(-1,2.4,2.01)
    glRotatef(90, 1,0,0)
    plataforma_plana(0.6,0.3,0,color_ventana)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(1,2.4,2.01)
    glRotatef(90, 1,0,0)
    plataforma_plana(0.6,0.3,0,color_ventana)
    glPopMatrix()
    


def infonavit(color_puerta=(0.5, 0.5, 0.5),  color_pared=(1.0, 1.0, 1.0), color_ventana=(0.0, 0.0, 0.0), escala=1.0,abrir=0.0):
    #cubo(alto, ancho, largo, color_lados, color_arriba, color_abajo)
    #plataforma_plana(lado1, lado2,altura, color=(1.0, 1.0, 1.0))
    #1.21, 0.6   

    #paredes
    cubo(3,4,4,color_pared,color_pared,color_pared)
    #ventanas
    glPushMatrix()
    glTranslatef(-1,2.4,2.01)
    glRotatef(90, 1,0,0)
    plataforma_plana(0.6,0.3,0,color_ventana)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(1,2.4,2.01)
    glRotatef(90, 1,0,0)
    plataforma_plana(0.6,0.3,0,color_ventana)
    glPopMatrix()
    

    #puertas
    #puerta izquierda
    glPushMatrix()
    glTranslatef(-abrir,0,0)
    glPushMatrix()
    glTranslatef(-0.3,1,2.01)
    glRotatef(90, 1,0,0)
    plataforma_plana(0.28,1,0,color_puerta)

    glPopMatrix()
    glPopMatrix()

    #puerta derecha
    glPushMatrix()
    glTranslatef(abrir,0,0)
    glPushMatrix()
    glTranslatef(0.3,1,2.01)
    glRotatef(90, 1,0,0)
    plataforma_plana(0.28,1,0,color_puerta)

    glPopMatrix()
    glPopMatrix()

    #puerta hoyo
    glPushMatrix()
    glTranslatef(0,1,2.005)
    glRotatef(90, 1,0,0)
    plataforma_plana(0.6,1,0,(0,0,0))
    glPopMatrix()
    
    

def torre_supersonica(altura=27.5, radio_base=0.8, radio_platillo=3.0, color=(0.4, 0.7, 0.95), escala=1.0):
    # Dibuja la torre
    glPushMatrix()
    # Aplicar escalamiento general
    glScalef(escala, escala, escala)
    
    t = glfw.get_time()
    angulo_giro = t * 50.0  # Velocidad de rotación
    
        
    # Pilar
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, radio_base * 0.35, altura, (0.8, 0.8, 0.85)) 
    glPopMatrix()
    
    # Anillos
    glPushMatrix()
    glTranslatef(0.0, altura * 0.45, 0.0)
    glRotatef(angulo_giro, 0.0, 1.0, 0.0) # Rotación sobre el eje vertical Y
    anillo_elipsoide(radio_base * 1.5, radio_base * 1.5, radio_base * 1.25, radio_base * 1.25, 360, 0.0, (1.0, 0.3, 0.3)) 
    anillo_elipsoide(radio_base * 1.8, radio_base * 1.8, radio_base * 1.7, radio_base * 1.7, 360, 0.2, (0.0, 0.9, 0.9)) 
    glPopMatrix()
    
    # Platillo principal 
    glPushMatrix()
    glTranslatef(0.0, altura - 1.2, 0.0)
    
    # Base inferior del platillo
    anillo_elipsoide(radio_platillo, radio_platillo, 0.0, 0.0, 360, 0.0, color)
    
    # Anillo exterior
    glPushMatrix()
    glRotatef(-angulo_giro * 1.5, 0.0, 1.0, 0.0)
    anillo_elipsoide(radio_platillo + 0.4, radio_platillo + 0.4, radio_platillo, radio_platillo, 360, 0.1, (0.85, 0.85, 0.9))
    glPopMatrix()
    
    # Cabina central 
    glPushMatrix()
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, radio_platillo * 0.7, 0.7, color)
    glPopMatrix()
    
    # Cúpula de cristal
    glPushMatrix()
    glTranslatef(0.0, 0.7, 0.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    esfera(radio_platillo * 0.55, (0.3, 0.9, 1.0, 0.45))
    glDisable(GL_BLEND)
    glPopMatrix()
    
    # Gran antena en la cima
    glPushMatrix()
    glTranslatef(0.0, 1.3, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, 0.04, 1.2, (1.0, 1.0, 0.4))
    glTranslatef(0.0, 0.0, 1.2)
    # Esfera de la antena
    esfera(0.18, (1.0, 0.1, 0.1))
    glPopMatrix()
    
    glPopMatrix() # Fin del platillo
    glPopMatrix() # Fin de la torre

def dibujar_torres():
    # Dibuja todas las torres de distintos tamaños

    #Torre más grandota
    """ glPushMatrix()
    glTranslatef(0.0, -20, 0.0)
    torre_supersonica(escala=1.3, color=(0.4, 0.7, 0.95))
    glPopMatrix() """

    # Torre Mediana 1
    glPushMatrix()
    glTranslatef(-16.0, -20, -12.0)
    torre_supersonica(escala=1.1, color=(1.0, 0.5, 0.3))
    glPopMatrix()

    # Torre Mediana 2 
    glPushMatrix()
    glTranslatef(16.0, -20, -12.0)
    torre_supersonica(escala=0.95, color=(0.3, 0.9, 0.75))
    glPopMatrix()

    # Torre Pequeña 1 
    glPushMatrix()
    glTranslatef(-10.0, -20, 10.0)
    torre_supersonica(escala=0.82, color=(0.85, 0.4, 0.9))
    glPopMatrix()

    # Torre Pequeña 2 
    glPushMatrix()
    glTranslatef(10.0, -20, 10.0)
    torre_supersonica(escala=0.75, color=(0.95, 0.85, 0.2))
    glPopMatrix()

def dibujar_infonavits_fila(color_pared=(1,1,1), color_ventana=(1,1,1), color_puerta=(1,1,1),desplazamiento=0):
    a=-20
    for i in range(10):
        glPushMatrix()
        glTranslatef(a-2, -20, -15+desplazamiento)
        infonavit(color_pared=color_pared,color_ventana=color_ventana,color_puerta=color_puerta,escala=1.0, abrir=0.0)
        glPopMatrix()
        a+=6
    a=-22
    for i in range (8):
        glPushMatrix()
        glTranslatef(a, -18, -15+desplazamiento)
        infonavit_sin_puerta(color_pared=color_pared,color_ventana=color_ventana,escala=1.0)
        glPopMatrix()
        a+=7
    a=-14
    for i in range (5):
        glPushMatrix()
        glTranslatef(a+8, -16, -15+desplazamiento)
        infonavit_sin_puerta(color_pared=color_pared,color_ventana=color_ventana,escala=1.0)
        glPopMatrix()
        a+=8
    

def dibujar_infonavits():
    dibujar_infonavits_fila(color_pared=(0.6,0.4,0.2), color_ventana=(0,1,1), color_puerta=(0.3,0.1,0.1))
    dibujar_infonavits_fila(color_pared=(0.5,0.5,0.5), color_ventana=(0,1,1), color_puerta=(0.3,0.1,0.1),desplazamiento=15)
    dibujar_infonavits_fila(color_pared=(0.7,0.5,0.5), color_ventana=(0,1,1), color_puerta=(0.3,0.1,0.1),desplazamiento=30)
    dibujar_infonavits_fila(color_pared=(0.8,0.6,0.4), color_ventana=(0,1,1), color_puerta=(0.3,0.1,0.1),desplazamiento=45)
 
def dibujar_basurero(x, y, z, color):
   
    glPushMatrix()
    glTranslatef(x, y, z)
    cubo(0.8, 0.5, 0.5, color, color, color)
    glTranslatef(0, 0.81, 0)
    cubo(0.05, 0.55, 0.55, (0.1, 0.1, 0.1), (0.1, 0.1, 0.1), (0.1, 0.1, 0.1))
    glPopMatrix()

def dibujar_basureros():
    for z_calle in [-7, 8, 23]:
        for idx, x in enumerate(range(-20, 20, 7)):
            dibujar_basurero(x, -20, z_calle - 2.5, (0.1, 0.5, 0.1))
            dibujar_basurero(x + 3.5, -20, z_calle + 2.5, (0.1, 0.5, 0.1))

def dibujar_monton_basura(x, y, z):
    # Monton de basura arrumbada 
    colores = [(0.4, 0.4, 0.3), (0.5, 0.4, 0.4), (0.3, 0.4, 0.4), (0.4, 0.5, 0.3), (0.35, 0.45, 0.4), (0.45, 0.35, 0.35)]
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Nivel base
    glPushMatrix()
    glTranslatef(0, 0.4, 0)
    glRotatef(15, 0, 1, 0)
    cubo(0.8, 1.0, 1.0, colores[0], colores[0], colores[0])
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0.8, 0.35, 0.6)
    glRotatef(-25, 0, 1, 0)
    cubo(0.7, 0.9, 0.8, colores[1], colores[1], colores[1])
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.6, 0.45, -0.4)
    glRotatef(40, 1, 1, 0)
    cubo(0.9, 0.8, 0.9, colores[2], colores[2], colores[2])
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0.6, 0.4, -0.7)
    glRotatef(-15, 0, 1, 0)
    cubo(0.8, 0.9, 0.7, colores[4], colores[4], colores[4])
    glPopMatrix()

    # Nivel medio
    glPushMatrix()
    glTranslatef(0.2, 1.2, 0.2)
    glRotatef(10, 1, 0, 1)
    cubo(0.8, 0.8, 0.8, colores[3], colores[3], colores[3])
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.2, 1.1, 0.5)
    glRotatef(-18, 1, 1, 0)
    cubo(0.7, 0.8, 0.7, colores[5], colores[5], colores[5])
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.4, 1.0, -0.3)
    glRotatef(30, 0, 0, 1)
    cubo(0.6, 0.7, 0.7, colores[0], colores[0], colores[0])
    glPopMatrix()

    # Nivel alto 
    glPushMatrix()
    glTranslatef(0.0, 1.8, 0.0)
    glRotatef(45, 1, 1, 1)
    cubo(0.6, 0.6, 0.6, colores[1], colores[1], colores[1])
    glPopMatrix()

    glPopMatrix()

def dibujar_basura_alrededores():
    # Montones de basura rodeando TODA la ciudad
    # Lado izquierdo y derecho 
    for z in range(-25, 45, 8):
        dibujar_monton_basura(-28, -20, z)
        dibujar_monton_basura(32, -20, z)
    
    # Lado frontal y trasero 
    for x in range(-25, 30, 8):
        dibujar_monton_basura(x, -20, -25)
        dibujar_monton_basura(x, -20, 42)

def dibujar_lata():
    glPushMatrix()
    # Centrar el cilindro 
    glTranslatef(0, 0, -0.2)
    cilindro_solido(0, 360, 0.2, 0.4, (0.8, 0.1, 0.1)) # Lata roja
    glPopMatrix()

def dibujar_lata_rodante():
    t = glfw.get_time()
    # Va y viene frente a las últimas casas.
    distancia = 15.0
    velocidad = 1.5
    ciclo = (t * velocidad) % (2.0 * distancia)
    
    if ciclo <= distancia:
        desplazamiento = ciclo - distancia / 2.0
        # Avanzando
        giro_lata = (ciclo * 360.0) / (2.0 * math.pi * 0.2)
    else:
        desplazamiento = distancia / 2.0 - (ciclo - distancia)
        # Regresando
        giro_lata = -(ciclo * 360.0) / (2.0 * math.pi * 0.2)

    glPushMatrix()
    # Posición frente a las casas (z=35, frente a la última fila z=30)
    glTranslatef(desplazamiento, -19.8, 35) 
    
    # Rota sobre Z para simular que rueda al moverse en X
    glRotatef(-giro_lata, 0, 0, 1)
    dibujar_lata()
    glPopMatrix()

  
 



# Elementos del cielo

ESTRELLAS = []
for _ in range(200):
    theta = random.uniform(0, 2 * math.pi)
    phi = random.uniform(0.1, math.pi / 2.2) 
    radio = random.uniform(70.0, 160.0)
    x = radio * math.cos(theta) * math.sin(phi)
    y = radio * math.cos(phi)
    z = radio * math.sin(theta) * math.sin(phi)
    ESTRELLAS.append((x, y, z))

def dibujar_estrellas():
    glDisable(GL_LIGHTING) # Para que brillen blancas sin sombra
    for (x, y, z) in ESTRELLAS:
        glPushMatrix()
        glTranslatef(x, y, z)
        esfera(0.3, (1.0, 1.0, 1.0))
        glPopMatrix()
    glEnable(GL_LIGHTING)

def dibujar_nubes():
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=-25, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=8
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=-20, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=15

    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=-15, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=9
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=-10, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=12
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=-5, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=10
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=0, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=15
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=5, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=9
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=10, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=12
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=15, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=8
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=20, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=15
    a=-20
    for i in range(40):
        animar_movimiento_lineal(
        lambda: nube(),
        x=a, y=-3, z=25, distancia=2.0, velocidad=0.3, eje_x=True
        )
        a+=9
   
    

def dibujar_nave_espacial(color=(0.9, 0.9, 0.9), color_cristal=(0.3, 0.8, 1.0, 0.55), escala=1.0):
    # Dibuja una nave
    t=glfw.get_time()

    glPushMatrix()
    glScalef(escala, escala, escala)
    
    cubo(0.3, 0.6, 1.8, color, color, color)
    
    # Cabina de mando
    glPushMatrix()
    glTranslatef(0.0, 0.18, 0.6)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    esfera(0.25, color_cristal)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    # Ala Derecha
    glPushMatrix()
    glTranslatef(0.5, 0.1, -0.15)
    cubo(0.04, 0.9, 0.7, color, color, color)
    glPopMatrix()
    
    # Ala Izquierda 
    glPushMatrix()
    glTranslatef(-0.5, 0.1, -0.15)
    cubo(0.04, 0.9, 0.7, color, color, color)
    glPopMatrix()
    
    # Propulsor
    glPushMatrix()
    glTranslatef(0.0, 0.1, -0.9)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, 0.14, 0.3, (0.45, 0.45, 0.5))
    glPopMatrix()
    
    # Fuego/Llama oscilante detrás del propulsor
    
    oscilacion_llama = 1.0 + 0.7 * math.sin(t * 35.0)
    glPushMatrix()
    glTranslatef(0.0, 0.1, -1.15)
    glScalef(1.0, 1.0, oscilacion_llama)
    glRotatef(180.0, 1.0, 0.0, 0.0)
    piramide(0.35, 0.16, 0.16, 0.0, (1.0, 0.35, 0.0))
    glPopMatrix()
    
    glPopMatrix()


def renderizar_flota_naves():
    # Renderiza todas las naves
    # Nave 1
    animar_vuelo_circular(
        lambda: dibujar_nave_espacial(color=(0.3, 0.8, 1.0), escala=1.1),
        centro_x=0.0, centro_z=0.0, altura=9.5, radio=22.0, velocidad=0.6, fase=0.0
    )
    
    # Nave 2
    animar_vuelo_circular(
        lambda: dibujar_nave_espacial(color=(1.0, 0.45, 0.15), escala=1.1),
        centro_x=0.0, centro_z=0.0, altura=9.5, radio=22.0, velocidad=0.6, fase=math.pi
    )

    # Nave 3
    animar_vuelo_circular(
        lambda: dibujar_nave_espacial(color=(0.85, 0.35, 0.9), escala=0.85),
        centro_x=0.0, centro_z=0.0, altura=8.0, radio=13.0, velocidad=-0.9, fase=1.5
    )

    # Nave 4
    animar_vuelo_circular(
        lambda: dibujar_nave_espacial(color=(0.2, 0.9, 0.65), escala=0.7),
        centro_x=-16.0, centro_z=-12.0, altura=6.5, radio=6.5, velocidad=-1.4, fase=0.5
    )

    # Nave 5
    animar_vuelo_circular(
        lambda: dibujar_nave_espacial(color=(0.95, 0.25, 0.25), escala=0.7),
        centro_x=16.0, centro_z=-12.0, altura=6.5, radio=6.5, velocidad=1.4, fase=2.0
    )

# Personas

def dibujar_persona_supersonica(color_cuerpo=(0.3, 0.7, 1.0), color_piel=(0.95, 0.8, 0.65), escala=1.0,
                                 ang_brazo_iz=0.0, ang_brazo_de=0.0, ang_pierna_iz=0.0, ang_pierna_de=0.0):
    # Dibuja una persona
    glPushMatrix()
    glScalef(escala, escala, escala)
    glRotatef(90,0,1,0) #Rotar a la persona 90° sobre el eje y
    # Cabeza (esfera)
    glPushMatrix()
    glTranslatef(0.0, 1.05, 0.0)
    esfera(0.15, color_piel)
    glPopMatrix()
    
    # Torso (cilindro vertical)
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, 0.1, 0.45, color_cuerpo)
    glPopMatrix()
    
    # Brazo izquierdo
    glPushMatrix()
    glTranslatef(-0.15, 0.9, 0.0)
    glRotatef(ang_brazo_iz, 1.0, 0.0, 0.0)
    glRotatef(90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, 0.04, 0.35, color_cuerpo)
    glPopMatrix()
    
    # Brazo derecho
    glPushMatrix()
    glTranslatef(0.15, 0.9, 0.0)
    glRotatef(ang_brazo_de, 1.0, 0.0, 0.0)
    glRotatef(90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, 0.04, 0.35, color_cuerpo)
    glPopMatrix()
    
    # Pierna izquierda
    glPushMatrix()
    glTranslatef(-0.06, 0.5, 0.0)
    glRotatef(ang_pierna_iz, 1.0, 0.0, 0.0)
    glRotatef(90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, 0.05, 0.5, color_cuerpo)
    glPopMatrix()
    
    # Pierna derecha
    glPushMatrix()
    glTranslatef(0.06, 0.5, 0.0)
    glRotatef(ang_pierna_de, 1.0, 0.0, 0.0)
    glRotatef(90.0, 1.0, 0.0, 0.0)
    cilindro_solido(0, 360, 0.05, 0.5, color_cuerpo)
    glPopMatrix()
    
    glPopMatrix()

def dibujar_persona_caminando(color_cuerpo=(0.3, 0.7, 1.0), color_piel=(0.95, 0.8, 0.65), escala=1.0):
    # Animar piernas y brazos de la persona al caminar
    t=glfw.get_time()
    oscilacion = 30.0 * math.sin(t * 4.0)  # ±30 grados a velocidad moderada
    
    dibujar_persona_supersonica(
        color_cuerpo=color_cuerpo, color_piel=color_piel, escala=escala,
        ang_brazo_iz=oscilacion, ang_brazo_de=-oscilacion,
        ang_pierna_iz=-oscilacion, ang_pierna_de=oscilacion
    )

def dibujar_patineta(color=(0.2, 0.2, 0.25)):
    # Dibuja la patineta
    glPushMatrix()
    # Tabla
    cubo(0.03, 0.2, 0.6, color, color, color)
    # Ruedas 
    for dx in [-0.07, 0.07]:
        for dz in [-0.2, 0.2]:
            glPushMatrix()
            glTranslatef(dx, -0.02, dz)
            esfera(0.03, (0.8, 0.8, 0.0))
            glPopMatrix()
    glPopMatrix()

def dibujar_persona_en_patineta(color_cuerpo=(0.9, 0.3, 0.5), color_piel=(0.95, 0.8, 0.65), escala=1.0,rotar_y=0):
    # Dibuja persona en la patineta
    glPushMatrix()
    glScalef(escala, escala, escala)
    glRotatef(rotar_y,0,1,0)
    
    # La patineta está al nivel del suelo
    dibujar_patineta()
    
    # Persona encima 
    glPushMatrix()
    glTranslatef(0.0, 0.03, 0.0)
    dibujar_persona_supersonica(
        color_cuerpo=color_cuerpo, color_piel=color_piel, escala=1.0,
        ang_brazo_iz=15.0, ang_brazo_de=-10.0,  
        ang_pierna_iz=5.0, ang_pierna_de=-5.0
    )
    glPopMatrix()
    
    glPopMatrix()


def robot_patrulla():
    # Dibuja un robot de patrulla
    color_chasis = (0.2, 0.2, 0.2)
    cubo(0.5, 0.6, 0.8, color_chasis, (0.3, 0.3, 0.3), (0.1, 0.1, 0.1))
    
    # Faro frontal 
    glPushMatrix()
    glTranslatef(0.0, 0.25, 0.4) 
    esfera(0.1, (0.0, 1.0, 1.0))
    glPopMatrix()
    
    # Propulsores laterales
    glPushMatrix()
    glTranslatef(0.35, 0.1, 0.0)
    cilindro_solido(0, 360, 0.15, 0.6, (0.1, 0.1, 0.1))
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-0.35, 0.1, 0.0)
    cilindro_solido(0, 360, 0.15, 0.6, (0.1, 0.1, 0.1))
    glPopMatrix()

def renderizar_millonarios():

    
    # Personas en patineta sobre el suelo
    
    # Skater 1
    animar_movimiento_lineal(
        lambda: dibujar_persona_en_patineta(color_cuerpo=(1.0, 0.3, 0.6), escala=0.9,rotar_y=90),
        x=0.0, y=0.01, z=6.0, distancia=12.0, velocidad=0.8, eje_x=True
    )
    
    # Skater 2
    animar_movimiento_lineal(
        lambda: dibujar_persona_en_patineta(color_cuerpo=(0.2, 0.9, 0.4), escala=0.85),
        x=-7.0, y=0.01, z=0.0, distancia=10.0, velocidad=1.1, eje_x=False
    )
    
    # Skater 3
    animar_movimiento_lineal(
        lambda: dibujar_persona_en_patineta(color_cuerpo=(0.95, 0.85, 0.15), escala=0.8,rotar_y=90),
        x=5.0, y=0.01, z=-8.0, distancia=8.0, velocidad=0.65, eje_x=True
    )


# Tuberías detrás

def tuberia_horizontal(x_inicio, longitud_x, y, z,
                       color_tubo=(0.08, 0.55, 0.08),
                       color_particula=(1.0, 0.92, 0.05)):
  
    glPushMatrix()
    glTranslatef(x_inicio, y, z)

    # Tubo horizontal principal 
    glPushMatrix()
    glRotatef(90.0, 0.0, 1.0, 0.0)   # Rotar
    cilindro_solido(0, 360, 0.18, longitud_x, color_tubo)
    glPopMatrix()

    # Tubo vertical emisor al final del tubo horizontal 
    glPushMatrix()
    glTranslatef(longitud_x, 0.0, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)  # Apuntar hacia arriba
    cilindro_solido(0, 360, 0.30, 2.8, color_tubo)
    glPopMatrix()

    # Partículas que emergen del extremo superior 
    t_local = glfw.get_time()
    for i in range(7):
        desfase = i * 0.50
        vel     = 2.6
        alt     = ((t_local * vel + desfase) % 2.4)
        if alt > 0.08:
            escala = max(0.0, 1.0 - alt / 2.4)
            desp_x = math.sin(t_local * 2.8 + i * 9) * 0.20
            desp_z = math.cos(t_local * 2.1 + i * 7) * 0.20
            glPushMatrix()
            glTranslatef(longitud_x + desp_x, 2.8 + alt, desp_z)
            esfera(0.16 * escala, color_particula)
            glPopMatrix()

    glPopMatrix()


def dibujar_tuberias_ciudad():
    """
    Tuberías horizontales verdes pegadas a la pared trasera de cada fila de infonavits.
    """
    COLOR_VERDE = (0.08, 0.52, 0.08)
    x_ini    = -25
    longitud = 60

    # calle 1
    tuberia_horizontal(x_ini, longitud, -19.5, -17.35,
                       color_tubo=COLOR_VERDE,
                       color_particula=(1.0, 0.92, 0.04))

    # calle 2
    tuberia_horizontal(x_ini, longitud, -19.5, -2.35,
                       color_tubo=COLOR_VERDE,
                       color_particula=(0.72, 0.04, 0.96))

    # calle 3
    tuberia_horizontal(x_ini, longitud, -19.5, 12.65,
                       color_tubo=COLOR_VERDE,
                       color_particula=(1.0, 0.92, 0.04))

    # calle 4
    tuberia_horizontal(x_ini, longitud, -19.5, 27.65,
                       color_tubo=COLOR_VERDE,
                       color_particula=(0.72, 0.04, 0.96))


#Animaciones

def animar_movimiento_lineal(dibujar_func, x, y, z, distancia, velocidad, eje_x=True):
    #Función general parametrizada para mover un objeto en ida y vuelta
    t=glfw.get_time()
    desplazamiento = distancia * math.sin(t * velocidad)
    
    glPushMatrix()
    if eje_x:
        glTranslatef(x + desplazamiento, y, z)
    else:
        glTranslatef(x, y, z + desplazamiento)
    
    dibujar_func()
    glPopMatrix()

def animar_patrullaje_lineal(dibujar_func, x_base, y_base, z_base, distancia, velocidad, eje_x=True):
    #Mueve un objeto en línea recta y da la vuelta al llegar al límite
    t = glfw.get_time()
    ciclo = (t * velocidad) % (2.0 * distancia)
    r_giro = 1.0  # Espacio en el que hace el giro
    
    if ciclo <= distancia:
        desplazamiento = ciclo - distancia / 2.0
        # Va para adelante
        if ciclo > distancia - r_giro:
            progreso = (ciclo - (distancia - r_giro)) / r_giro
            angulo_rotacion = 90.0 * progreso
        elif ciclo < r_giro:
            progreso = ciclo / r_giro
            angulo_rotacion = 270.0 + 90.0 * progreso
        else:
            angulo_rotacion = 0.0
    else:
        desplazamiento = distancia / 2.0 - (ciclo - distancia)
        # Va de regreso
        if ciclo < distancia + r_giro:
            progreso = (ciclo - distancia) / r_giro
            angulo_rotacion = 90.0 + 90.0 * progreso
        elif ciclo > 2.0 * distancia - r_giro:
            progreso = (ciclo - (2.0 * distancia - r_giro)) / r_giro
            angulo_rotacion = 180.0 + 90.0 * progreso
        else:
            angulo_rotacion = 180.0

    glPushMatrix()
    if eje_x:
        glTranslatef(x_base + desplazamiento, y_base, z_base)
        glRotatef(angulo_rotacion, 0.0, 1.0, 0.0)
    else:
        glTranslatef(x_base, y_base, z_base + desplazamiento)
        glRotatef(90.0 + angulo_rotacion, 0.0, 1.0, 0.0)

    dibujar_func()
    glPopMatrix()



def animar_patrullaje_persona(color_cuerpo, color_piel, escala,
                              x_base, y_base, z_base, distancia, velocidad, eje_x=True):
    #Mueve a la persona en línea recta y la hace girar
    t = glfw.get_time()
    ciclo = (t * velocidad) % (2.0 * distancia)
    r_giro = 1.0 
    
    if ciclo <= distancia:
        desplazamiento = ciclo - distancia / 2.0
        if ciclo > distancia - r_giro:
            progreso = (ciclo - (distancia - r_giro)) / r_giro
            angulo_rotacion = 90.0 * progreso
        elif ciclo < r_giro:
            progreso = ciclo / r_giro
            angulo_rotacion = 270.0 + 90.0 * progreso
        else:
            angulo_rotacion = 0.0
    else:
        desplazamiento = distancia / 2.0 - (ciclo - distancia)
        if ciclo < distancia + r_giro:
            progreso = (ciclo - distancia) / r_giro
            angulo_rotacion = 90.0 + 90.0 * progreso
        elif ciclo > 2.0 * distancia - r_giro:
            progreso = (ciclo - (2.0 * distancia - r_giro)) / r_giro
            angulo_rotacion = 180.0 + 90.0 * progreso
        else:
            angulo_rotacion = 180.0

    ang_base = 0.0 if eje_x else 90.0
    angulo_final = ang_base + angulo_rotacion

    glPushMatrix()
    if eje_x:
        glTranslatef(x_base + desplazamiento, y_base, z_base)
    else:
        glTranslatef(x_base, y_base, z_base + desplazamiento)

    glRotatef(angulo_final, 0.0, 1.0, 0.0)
    dibujar_persona_caminando(color_cuerpo=color_cuerpo, color_piel=color_piel, escala=escala)
    glPopMatrix()



def animar_vuelo_circular(dibujar_objeto_func, centro_x, centro_z, altura, radio, velocidad, fase=0.0):
    #Animación de vuelo circular
    t=glfw.get_time()
    angulo = t * velocidad + fase
    
    x = centro_x + radio * math.cos(angulo)
    z = centro_z + radio * math.sin(angulo)
    
    # Tangente del círculo: derivada de (cos(θ), sin(θ)) = (-sin(θ), cos(θ))
    # Multiplicada por el signo de la velocidad para invertir si va en sentido contrario
    signo = 1.0 if velocidad >= 0 else -1.0
    tx = -math.sin(angulo) * signo
    tz = math.cos(angulo) * signo
    
    # Ángulo de orientación en grados (atan2 nos da el ángulo desde +Z hacia +X)
    angulo_orientacion = math.degrees(math.atan2(tx, tz))
    
    glPushMatrix()
    glTranslatef(x, altura, z)
    glRotatef(angulo_orientacion, 0.0, 1.0, 0.0)
    dibujar_objeto_func()
    glPopMatrix()

# Semáforos en las calles

def dibujar_semaforos():
    #Posiciones de semaforos
    posiciones = [
        # Calle 1 (z ≈ -7)
        (-10, 7, -7),
        (  2, 7, -7),
        ( 12, 7, -7),
        # Calle 2 (z ≈ 8)
        (-10, 7,  8),
        (  2, 7,  8),
        ( 12, 6,  8),
        # Calle 3 (z ≈ 23)
        (-10, 7, 23),
        (  4, 7, 23),
    ]
    for (px, py, pz) in posiciones:
        glPushMatrix()
        glTranslatef(px, py, pz)
        semaforo()
        glPopMatrix()


#Personas caminando por las calles

def dibujar_personas_calles():
   
    #Personas que caminan por las caller entre las filas de casas.

    colores = [
        ((0.3, 0.4, 0.5),  (0.95, 0.80, 0.65)),
        ((0.5, 0.3, 0.3),  (0.95, 0.80, 0.65)),
        ((0.3, 0.5, 0.3),  (0.90, 0.75, 0.60)),
        ((0.5, 0.4, 0.2),  (0.95, 0.80, 0.65)),
        ((0.4, 0.3, 0.4),  (0.95, 0.80, 0.65)),
        ((0.3, 0.4, 0.4),  (0.92, 0.78, 0.62)),
    ]

    # Calle 1
    for idx, (cc, cp) in enumerate(colores):
        x_base = -12 + idx * 5
        animar_patrullaje_persona(
            color_cuerpo=cc, color_piel=cp, escala=0.85,
            x_base=x_base, y_base=-20, z_base=-7,
            distancia=8.0, velocidad=0.8 + idx * 0.15, eje_x=True
        )

    # Calle 2
    for idx, (cc, cp) in enumerate(colores):
        x_base = -14 + idx * 5
        animar_patrullaje_persona(
            color_cuerpo=cc, color_piel=cp, escala=0.85,
            x_base=x_base, y_base=-20, z_base=8,
            distancia=8.0, velocidad=0.7 + idx * 0.12, eje_x=True
        )

    # Calle 3
    for idx, (cc, cp) in enumerate(colores[:4]):
        x_base = -10 + idx * 7
        animar_patrullaje_persona(
            color_cuerpo=cc, color_piel=cp, escala=0.85,
            x_base=x_base, y_base=-20, z_base=23,
            distancia=8.0, velocidad=0.9 + idx * 0.1, eje_x=True
        )


#Camaras en cada calle

def dibujar_camaras_calles():
    posiciones_camaras = [
        (-18, -20, -8),   # Calle 1 izquierdo
        ( 18, -20, -8),   # Calle 1 derecho
        (-18, -20,  8),   # Calle 2 izquierdo
        ( 18, -20,  8),   # Calle 2 derecho
        (-18, -20, 22),   # Calle 3 izquierdo
        ( 18, -20, 22),   # Calle 3 derecho
    ]
    for (cx, cy, cz) in posiciones_camaras:
        camara_vigilancia_rotatoria(cx, cy, cz)

#Drones en cada calle

def dibujar_drones_calles():
    #Drones que patrullan en línea recta a lo largo de cada calle.
    
    # Dron 1
    animar_patrullaje_lineal(
        lambda: dron_policial(0, 0, 0),
        x_base=0.0, y_base=-15.5, z_base=-7.0,
        distancia=18.0, velocidad=3.0, eje_x=True
    )
    # Dron 2
    animar_patrullaje_lineal(
        lambda: dron_policial(0, 0, 0),
        x_base=0.0, y_base=-15.0, z_base=8.0,
        distancia=18.0, velocidad=2.7, eje_x=True
    )
    # Dron 3
    animar_patrullaje_lineal(
        lambda: dron_policial(0, 0, 0),
        x_base=0.0, y_base=-14.5, z_base=23.0,
        distancia=18.0, velocidad=3.3, eje_x=True
    )
    # Dron 4
    animar_patrullaje_lineal(
        lambda: dron_policial(0, 0, 0),
        x_base=-20.0, y_base=-15.0, z_base=8.0,
        distancia=15.0, velocidad=2.5, eje_x=False
    )
    # Dron 5
    animar_patrullaje_lineal(
        lambda: dron_policial(0, 0, 0),
        x_base=20.0, y_base=-15.0, z_base=8.0,
        distancia=15.0, velocidad=2.8, eje_x=False
    )


#Renderizar escena completa

def renderizar_escena_completa():
    """Dibuja el entorno completo: plataforma, torres, naves y habitantes."""

    # Semáforos flotando por las calles
    dibujar_semaforos()

    dibujar_estrellas()
    dibujar_infonavits()
    dibujar_nubes()

    #Territorio grande central 
    plataforma_plana(42.0, 42.0, -20, (0.12, 0.16, 0.24))
    
    #Bordes 
    anillo_elipsoide(35.0, 35.0, 34.7, 34.7, 360, 0.005, (0.0, 1.0, 0.7))
    
    #Renderizar las torres
    dibujar_torres()
    
    # Renderizar la flota de naves
    renderizar_flota_naves()
    
    # Renderizar los habitantes 
    renderizar_millonarios()

    # Personas caminando por las calles con vuelta
    dibujar_personas_calles()

    # Cámaras de vigilancia
    dibujar_camaras_calles()

    # Drones patrullando 
    dibujar_drones_calles()

    # Tuberías
    dibujar_tuberias_ciudad()

    # Basureros
    dibujar_basureros()

    # Montones de basura 
    dibujar_basura_alrededores()
    
    #Lata rodando
    dibujar_lata_rodante()

    #Monstruo
    monstruo()
# Funcion principal 
def main(): 
    global moverx, movery, moverz, dx, dz, girar 

    try: 
        window = init_glfw() 
    except Exception as e: 
        print(f" Error al inicializar GLFW: {e}") 
        return 

    setup_opengl() 
    setup_lights() 

    frame_count = 0 
    fps_timer = glfw.get_time() 

    velocidad_manos_lados = 0.8
    velocidad_manos_giro = 0.08
    velocidad_manos_zoom = 1.0
    velocidad_manos_y = 1.0 

    bg_texture = create_video_texture()

    try: 
        cap = cv2.VideoCapture(0) 
        cv2.waitKey(2000) 

        while not glfw.window_should_close(window): 
            ret, frame = cap.read()
            if not ret: 
                break 
            
            frame = cv2.flip(frame, 1)
            frame2 = frame.copy() 
            h, w, _ = frame.shape 

            # --- DETECCIÓN DE RECTÁNGULO BLANCO ROBUSTA ---
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Umbralización usando Otsu con fallback para separar la hoja brillante del fondo
            otsu_thresh, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if otsu_thresh < 100 or otsu_thresh > 180:
                _, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)
            
            # Operación morfológica de clausura para rellenar huecos y conectar contornos rotos
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            paper_contour = None
            max_area = 0
            for c in contours:
                area = cv2.contourArea(c)
                if area > 4000:
                    # Envoltura convexa para ignorar dedos y ruido
                    hull = cv2.convexHull(c)
                    peri = cv2.arcLength(hull, True)
                    approx = cv2.approxPolyDP(hull, 0.03 * peri, True)
                    
                    if len(approx) == 4:
                        # Calcular la relación de aspecto del rectángulo para descartar líneas largas/delgadas
                        rect = cv2.minAreaRect(approx)
                        (cx_r, cy_r), (w_r, h_r), angle = rect
                        if w_r > 0 and h_r > 0:
                            aspect_ratio = max(w_r, h_r) / min(w_r, h_r)
                            # Un rectángulo de papel tiene típicamente un aspect ratio < 1.8
                            if aspect_ratio < 1.8:
                                # Analizar color en HSV: debe ser muy blanco (baja saturación, alto brillo)
                                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                                mask = np.zeros(gray.shape, dtype=np.uint8)
                                cv2.drawContours(mask, [approx], -1, 255, -1)
                                mean_val = cv2.mean(hsv, mask=mask)
                                mean_s = mean_val[1] # Saturación promedio (blanco < 60)
                                mean_v = mean_val[2] # Brillo promedio (blanco > 130)
                                
                                if mean_s < 60 and mean_v > 130:
                                    if area > max_area:
                                        paper_contour = approx
                                        max_area = area

            if paper_contour is not None:
                cv2.drawContours(frame2, [paper_contour], -1, (0, 255, 0), 3)
            # ---------------------------------------- 
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
            results = hands.process(frame_rgb) 

            dx = math.sin(girar)
            dz = -math.cos(girar)

            zona_y_arriba = 0.35
            zona_y_abajo = 0.65
            zona_x_izq = 0.35
            zona_x_der = 0.65
            
            cv2.line(frame2, (0, int(h*zona_y_arriba)), (w, int(h*zona_y_arriba)), (255, 0, 0), 1)
            cv2.line(frame2, (0, int(h*zona_y_abajo)), (w, int(h*zona_y_abajo)), (255, 0, 0), 1)
            cv2.line(frame2, (int(w*zona_x_izq), 0), (int(w*zona_x_izq), h), (255, 0, 0), 1)
            cv2.line(frame2, (int(w*zona_x_der), 0), (int(w*zona_x_der), h), (255, 0, 0), 1)

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    mp_drawing.draw_landmarks(frame2, hand_landmarks, mp_hands.HAND_CONNECTIONS) 
                    
                    label = "Left" if handedness.classification[0].label == "Right" else "Right"

                    cx = hand_landmarks.landmark[9].x
                    cy = hand_landmarks.landmark[9].y

                    if label == "Right":
                        if cy < zona_y_arriba: 
                            moverx += dx * velocidad_manos_zoom
                            moverz += dz * velocidad_manos_zoom
                        elif cy > zona_y_abajo: 
                            moverx -= dx * velocidad_manos_zoom
                            moverz -= dz * velocidad_manos_zoom
                        
                        if cx < zona_x_izq: 
                            moverx += dz * velocidad_manos_lados
                            moverz += -dx * velocidad_manos_lados
                        elif cx > zona_x_der: 
                            moverx -= dz * velocidad_manos_lados
                            moverz -= -dx * velocidad_manos_lados

                    if label == "Left":
                        if cx < zona_x_izq: 
                            girar -= velocidad_manos_giro
                        elif cx > zona_x_der: 
                            girar += velocidad_manos_giro
                            
                        if cy < zona_y_arriba: 
                            movery += velocidad_manos_y
                        elif cy > zona_y_abajo: 
                            movery -= velocidad_manos_y

            frame_bg_opengl = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            frame_bg_opengl = cv2.flip(frame_bg_opengl, 0)

            if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
                moverx += dx
                moverz += dz

            if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
                moverx -= dx
                moverz -= dz

            if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
                moverx += dz
                moverz -= dx

            if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
                moverx -= dz
                moverz += dx

            if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
                movery += 1

            if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
                movery -= 1

            if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
                girar -= 0.2

            if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
                girar += 0.2

            dx = math.sin(girar) 
            dz = -math.cos(girar)     

            glfw.poll_events() 

            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS: 
                break 

            glClearColor(r, g, b, 0) 
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 

            glBindTexture(GL_TEXTURE_2D, bg_texture)


            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, frame_bg_opengl)

            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)
            glEnable(GL_TEXTURE_2D)

            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, 1, 0, 1)

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

            glColor4f(1.0, 1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(0.0, 0.0)
            glTexCoord2f(1.0, 0.0); glVertex2f(1.0, 0.0)
            glTexCoord2f(1.0, 1.0); glVertex2f(1.0, 1.0)
            glTexCoord2f(0.0, 1.0); glVertex2f(0.0, 1.0)
            glEnd()

            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glDisable(GL_TEXTURE_2D)

            # Ajustar Viewport al tamaño actual de la ventana
            win_w, win_h = glfw.get_window_size(window)
            glViewport(0, 0, win_w, win_h)

            if paper_contour is not None:
                img_pts = paper_contour.reshape(4, 2).astype(np.float32)
                
                # Ordenar puntos: top-left, top-right, bottom-right, bottom-left
                img_pts = img_pts[np.argsort(img_pts[:, 0])]
                left_pair = img_pts[:2]
                right_pair = img_pts[2:]
                
                top_left = left_pair[np.argmin(left_pair[:, 1])]
                bottom_left = left_pair[np.argmax(left_pair[:, 1])]
                top_right = right_pair[np.argmin(right_pair[:, 1])]
                bottom_right = right_pair[np.argmax(right_pair[:, 1])]
                
                ordered_pts = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)

                # Definimos los puntos 3D correspondientes a la hoja (plano Z=0)
                # Coinciden con las dimensiones reales de la base de la ciudad (42.0 * 2 = 84.0)
                obj_pts = np.array([
                    [-42.0, -42.0, 0.0],
                    [ 42.0, -42.0, 0.0],
                    [ 42.0,  42.0, 0.0],
                    [-42.0,  42.0, 0.0]
                ], dtype=np.float32)

                focal_length = w
                center = (w / 2.0, h / 2.0)
                camera_matrix = np.array([
                    [focal_length, 0.0, center[0]],
                    [0.0, focal_length, center[1]],
                    [0.0, 0.0, 1.0]
                ], dtype=np.float64)
                
                dist_coeffs = np.zeros((4, 1))

                success, rvec, tvec = cv2.solvePnP(obj_pts, ordered_pts, camera_matrix, dist_coeffs)

                if success:
                    rmat, _ = cv2.Rodrigues(rvec)
                    view_matrix = np.eye(4, dtype=np.float64)
                    view_matrix[0:3, 0:3] = rmat
                    view_matrix[0:3, 3] = tvec.flatten()

                    # Convertir coordenadas OpenCV (Y abajo, Z adelante) a OpenGL (Y arriba, Z atrás)
                    cv_to_gl = np.array([
                        [1,  0,  0, 0],
                        [0, -1,  0, 0],
                        [0,  0, -1, 0],
                        [0,  0,  0, 1]
                    ], dtype=np.float64)
                    
                    view_matrix = np.dot(cv_to_gl, view_matrix)
                    view_matrix = view_matrix.T

                    fov_y = 2.0 * math.atan((h / 2.0) / focal_length)
                    fov_y_deg = math.degrees(fov_y)
                    
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()
                    gluPerspective(fov_y_deg, w / h, 0.1, 1000.0)

                    glMatrixMode(GL_MODELVIEW)
                    glLoadIdentity()
                    glLoadMatrixd(view_matrix.flatten())
                    
                    glPushMatrix()
                    glRotatef(-90, 1, 0, 0) 
                    glTranslatef(0.0, 20.0, 0.0) # Alinear la base de la ciudad (y = -20) al nivel de la hoja (y = 0)
                    renderizar_escena_completa()
                    glPopMatrix()
                else:
                    pass
            else:
                pass
            
            glfw.swap_buffers(window) 

            frame_count += 1 
            current_time = glfw.get_time() 
            if current_time - fps_timer >= 1.0: 
                fps = frame_count / (current_time - fps_timer) 
                glfw.set_window_title(window, f"{WINDOW_TITLE} - FPS: {fps:.1f}") 
                frame_count = 0 
                fps_timer = current_time 

    except Exception as e: 
        print(f" Error en el loop principal: {e}") 
        import traceback 
        traceback.print_exc() 

    finally: 
        print("\nCerrando aplicación...") 
        glDeleteTextures(1, [bg_texture])
        cap.release() 
        cv2.destroyAllWindows() 
        glfw.terminate()
if __name__ == "__main__": 

    main()
