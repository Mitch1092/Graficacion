import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import sys

tex_pasto = None
tex_pared = None
tex_techo = None

# Variables globales para la cámara
camera_pos = [4.0, 3.0, 8.0]  # Posición de la cámara
camera_target = [0.0, 1.0, 0.0]  # Punto al que mira
camera_up = [0.0, 1.0, 0.0]  # Vector hacia arriba

# Variables para el movimiento
camera_speed = 0.2  # Velocidad de movimiento
keys = {}  # Diccionario para controlar el estado de las teclas

def load_texture(path):
   
    img = Image.open(path).convert("RGB")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.tobytes()

    tex_id = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glBindTexture(GL_TEXTURE_2D, tex_id)

    # Filtrado suave + mipmaps
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Repetición
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Cargar textura normal
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                 img.width, img.height, 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)

    # Generar mipmaps moderno (reemplaza a gluBuild2DMipmaps)
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)

    return tex_id

def init():
	global tex_pasto, tex_pared, tex_techo
	"""Configuración inicial de OpenGL"""
	glClearColor(0.5, 0.8, 1.0, 1.0)  # Fondo azul cielo
	glEnable(GL_DEPTH_TEST)           # Activar prueba de profundidad
	glEnable(GL_TEXTURE_2D)
	
	# Configuración de la perspectiva
	glMatrixMode(GL_PROJECTION)
	gluPerspective(60, 1.0, 0.1, 100.0)  # Campo de visión más amplio
	glMatrixMode(GL_MODELVIEW)
	
	# Cargar texturas
	tex_pasto = load_texture("/home/michael/MEGA/Materias/Graficacion/Tareas/resources/pasto.png")
	tex_pared = load_texture("/home/michael/MEGA/Materias/Graficacion/Tareas/resources/pared.png")
	tex_techo = load_texture("/home/michael/MEGA/Materias/Graficacion/Tareas/resources/trunk.png")
    
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
	glBindTexture(GL_TEXTURE_2D, tex_pared)
	"""Dibuja el cubo (base de la casa)"""
	glBegin(GL_QUADS)
	glColor3f(0.8, 0.5, 0.2)  # Marrón para todas las caras

	# Frente
	glTexCoord2f(0, 0); glVertex3f(-1, 0, 1)
	glTexCoord2f(1, 0); glVertex3f( 1, 0, 1)
	glTexCoord2f(1, 1); glVertex3f( 1, 1, 1)
	glTexCoord2f(0, 1); glVertex3f(-1, 1, 1)

	# Atrás
	glTexCoord2f(0, 0); glVertex3f(-1, 0,-1)
	glTexCoord2f(1, 0); glVertex3f( 1, 0,-1)
	glTexCoord2f(1, 1); glVertex3f( 1, 1,-1)
	glTexCoord2f(0, 1); glVertex3f(-1, 1,-1)

	# Izquierda
	glTexCoord2f(0, 0); glVertex3f(-1, 0,-1)
	glTexCoord2f(1, 0); glVertex3f(-1, 0, 1)
	glTexCoord2f(1, 1); glVertex3f(-1, 1, 1)
	glTexCoord2f(0, 1); glVertex3f(-1, 1,-1)

	# Derecha
	glTexCoord2f(0, 0); glVertex3f( 1, 0,-1)
	glTexCoord2f(1, 0); glVertex3f( 1, 0, 1)
	glTexCoord2f(1, 1); glVertex3f( 1, 1, 1)
	glTexCoord2f(0, 1); glVertex3f( 1, 1,-1)

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
	glBindTexture(GL_TEXTURE_2D, 0)

def draw_roof():
	glBindTexture(GL_TEXTURE_2D, tex_techo)
	"""Dibuja el techo (pirámide)"""
	glBegin(GL_TRIANGLES)
	glColor3f(0.9, 0.1, 0.1)  # Rojo brillante

	# Frente
	glTexCoord2f(0, 0); glVertex3f(-1, 1, 1)
	glTexCoord2f(1, 0); glVertex3f(1, 1, 1)
	glTexCoord2f(0.5, 1); glVertex3f(0, 2, 0)

	# Atrás
	glTexCoord2f(0, 0); glVertex3f(-1, 1, -1)
	glTexCoord2f(1, 0); glVertex3f(1, 1, -1)
	glTexCoord2f(0.5, 1); glVertex3f(0, 2, 0)

	# Izquierda
	glTexCoord2f(0, 0); glVertex3f(-1, 1, -1)
	glTexCoord2f(1, 0); glVertex3f(-1, 1, 1)
	glTexCoord2f(0.5, 1); glVertex3f(0, 2, 0)

	# Derecha
	glTexCoord2f(0, 0); glVertex3f(1, 1, -1)
	glTexCoord2f(1, 0); glVertex3f(1, 1, 1)
	glTexCoord2f(0.5, 1); glVertex3f(0, 2, 0)
	glEnd()
	glBindTexture(GL_TEXTURE_2D, 0)

def draw_ground():
	glBindTexture(GL_TEXTURE_2D, tex_pasto)
	"""Dibuja un plano para representar el suelo o calle"""
	glBegin(GL_QUADS)
	glColor3f(0.3, 0.3, 0.3)  # Gris oscuro para la calle
	
	# Coordenadas del plano
	glVertex3f(-10, 0, 10)
	glVertex3f(10, 0, 10)
	glVertex3f(10, 0, -10)
	glVertex3f(-10, 0, -10)
	glEnd()
	
	glBindTexture(GL_TEXTURE_2D, 0)

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
