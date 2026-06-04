import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_triangle():
    # Dibuja un triángulo con OpenGL
    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.0, 0.0)  # Rojo
    glVertex2f(-0.5, -0.5)    # Vértice inferior izquierdo
    glColor3f(0.0, 1.0, 0.0)  # Verde
    glVertex2f(0.5, -0.5)     # Vértice inferior derecho
    glColor3f(0.0, 0.0, 1.0)  # Azul
    glVertex2f(0.0, 0.5)      # Vértice superior
    glEnd()

def main():
    # Inicializa GLFW
    if not glfw.init():
        return

    # Crear la ventana
    window = glfw.create_window(800, 600, "OpenGL Triángulo", None, None)
    if not window:
        glfw.terminate()
        return

    # Hacer el contexto de OpenGL actual para la ventana
    glfw.make_context_current(window)

    # Configurar la proyección (2D simple)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)  # Proyección ortográfica 2D
    glMatrixMode(GL_MODELVIEW)

    # Bucle principal
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)  # Limpiar la pantalla con color de fondo

        draw_triangle()  # Dibujar el triángulo

        glfw.swap_buffers(window)  # Intercambiar los buffers
        glfw.poll_events()  # Comprobar eventos

    # Finalizar GLFW
    glfw.terminate()

if __name__ == "__main__":
    main()
