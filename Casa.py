import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

# Variables globales para la cámara
camera_pos = [4.0, 3.0, 8.0]  # Posición de la cámara
camera_target = [0.0, 1.0, 0.0]  # Punto al que mira
camera_up = [0.0, 1.0, 0.0]  # Vector hacia arriba

# Variables para el movimiento
camera_speed = 0.2  # Velocidad de movimiento
keys = {}  # Diccionario para controlar el estado de las teclas

def init():
    """Configuración inicial de OpenGL"""
    glClearColor(0.5, 0.8, 1.0, 1.0)  # Fondo azul cielo
    glEnable(GL_DEPTH_TEST)           # Activar prueba de profundidad

    # Configuración de la perspectiva
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1.0, 0.1, 100.0)  # Campo de visión más amplio
    glMatrixMode(GL_MODELVIEW)
    
def draw_tree(x,z):
	draw_foliage(x,z)
	draw_trunk(x,z)    

def draw_trunk(x,z):
    """Dibuja el tronco del árbol como un cilindro"""
    glPushMatrix()
    glColor3f(0.6, 0.3, 0.1)  # Marrón para el tronco
    glTranslatef(x, 0, z)  # Posicionar el tronco
    glRotatef(-90, 1, 0, 0)  # Rota para orientar el cilindro verticalmente
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.3, 0.3, 2.0, 32, 32)  # Radio y altura del cilindro
    glPopMatrix()

def draw_foliage(x,z):
    """Dibuja las hojas del árbol como una esfera"""
    glPushMatrix()
    glColor3f(0.1, 0.8, 0.1)  # Verde para las hojas
    glTranslatef(x, 2, z)  # Posicionar las hojas encima del tronco
    quadric = gluNewQuadric()
    gluSphere(quadric, 1.0, 32, 32)  # Radio de la esfera
    glPopMatrix()
    
def draw_window():
	glBegin(GL_QUADS)
	glColor3f(0,0,1)
	glVertex3f(1.05, 0.5, -0.5)
	glVertex3f(1.05, 0.5, 0.5)
	glVertex3f(1.05, 0.8, 0.5)
	glVertex3f(1.05, 0.8, -0.5)
	glEnd()
	
def draw_garage():	
	glBegin(GL_QUADS)
	glColor3f(0.6,0.4,0.3)
	glVertex3f(-0.5, 0, 1.05)
	glVertex3f(0.5, 0, 1.05)	
	glVertex3f(0.5, 0.5, 1.05)
	glVertex3f(-0.5, 0.5, 1.05)
	glEnd()
	
	
def draw_cube():
    """Dibuja el cubo (base de la casa)"""
    glBegin(GL_QUADS)
    glColor3f(0.8, 0.5, 0.2)  # Marrón para todas las caras

    # Frente
    glVertex3f(-1, 0, 1)
    glVertex3f(1, 0, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)

    # Atrás
    glVertex3f(-1, 0, -1)
    glVertex3f(1, 0, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(-1, 1, -1)

    # Izquierda
    glVertex3f(-1, 0, -1)
    glVertex3f(-1, 0, 1)
    glVertex3f(-1, 1, 1)
    glVertex3f(-1, 1, -1)

    # Derecha
    glVertex3f(1, 0, -1)
    glVertex3f(1, 0, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(1, 1, -1)

    # Arriba
    glColor3f(0.9, 0.6, 0.3)  # Color diferente para el techo
    glVertex3f(-1, 1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)

    # Abajo
    glColor3f(0.6, 0.4, 0.2)  # Suelo más oscuro
    glVertex3f(-1, 0, -1)
    glVertex3f(1, 0, -1)
    glVertex3f(1, 0, 1)
    glVertex3f(-1, 0, 1)
    glEnd()

def draw_roof():
    """Dibuja el techo (pirámide)"""
    glBegin(GL_TRIANGLES)
    glColor3f(0.9, 0.1, 0.1)  # Rojo brillante

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
    """Dibuja un plano para representar el suelo o calle"""
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)  # Gris oscuro para la calle

    # Coordenadas del plano
    glVertex3f(-10, 0, 10)
    glVertex3f(10, 0, 10)
    glVertex3f(10, 0, -10)
    glVertex3f(-10, 0, -10)
    glEnd()

def draw_house():
	"""Dibuja una casa sobre un plano"""
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()

    # Configuración de la cámara
	gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],  # Posición de la cámara
              camera_target[0], camera_target[1], camera_target[2],  # Punto al que mira
              camera_up[0], camera_up[1], camera_up[2])  # Vector hacia arriba
	draw_ground()  # Dibuja el suelo
	draw_cube()    # Dibuja la base de la casa
	draw_roof()    # Dibuja el techo
	draw_garage()
	draw_window()
	draw_tree(3,2)
	draw_tree(4,0)
	draw_tree(-2,-2)
	
	glfw.swap_buffers(window)

def process_input():
	"""Procesa el estado de las teclas para mover la cámara"""
	global camera_pos

	if keys.get(glfw.KEY_W, False):  # Mover hacia adelante
		camera_pos[2] -= camera_speed
	if keys.get(glfw.KEY_S, False):  # Mover hacia atrás
		camera_pos[2] += camera_speed
	if keys.get(glfw.KEY_A, False):  # Mover a la izquierda
		camera_pos[0] -= camera_speed
	if keys.get(glfw.KEY_D, False):  # Mover a la derecha
		camera_pos[0] += camera_speed
	if keys.get(glfw.KEY_UP, False):  # Subir
		camera_pos[1] += camera_speed
	if keys.get(glfw.KEY_DOWN, False):  # Bajar
		camera_pos[1] -= camera_speed
        
def key_callback(window, key, scancode, action, mods):
    """Actualiza el estado de las teclas"""
    if action == glfw.PRESS:
        keys[key] = True
    elif action == glfw.RELEASE:
        keys[key] = False
        
def main():
	global window

    # Inicializar GLFW
	if not glfw.init():
		sys.exit()
    
    # Crear ventana de GLFW
	width, height = 800, 600
	window = glfw.create_window(width, height, "Casa 3D con Base", None, None)
	if not window:
		glfw.terminate()
		sys.exit()

	glfw.make_context_current(window)
	glViewport(0, 0, width, height)
	init()
	
	
    # Configurar callback de teclado
	glfw.set_key_callback(window, key_callback)

    # Bucle principal
	while not glfw.window_should_close(window):
		process_input()
		draw_house()
		glfw.poll_events()
		
	glfw.terminate()

if __name__ == "__main__":
	main()
