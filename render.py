# http://www.de-brauwer.be/wiki/wikka.php?wakka=PyOpenGLSierpinski

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window_id = -1

def draw_pixel_centre(x,y):
    # draw centre of each pixel
    glColor3ub(0, 255, 0)
    glBegin(GL_POINTS)
    glVertex2f(IMAGE_SCALE*(x+0.5), IMAGE_SCALE*(y+0.5))
    glEnd()

def init_original():
    global w,h
    ww = w * IMAGE_SCALE
    hh = h * IMAGE_SCALE
    glClearColor(1.0, 1.0, 1.0, 0.0)
    glColor3f(0.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, ww, 0, hh)
    glPointSize(3)

def display_original():
    global im
    w, h = im.size
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    for x in xrange(w):
        for y in xrange(h):
            r, g, b = get_node(x, y, im).rgb
            y = h - y - 1
            glColor3ub(r, g, b)
            glBegin(GL_QUADS)
            glVertex2f(IMAGE_SCALE*x, IMAGE_SCALE*y)
            glVertex2f(IMAGE_SCALE*(x+1), IMAGE_SCALE*y)
            glVertex2f(IMAGE_SCALE*(x+1), IMAGE_SCALE*(y+1))
            glVertex2f(IMAGE_SCALE*x, IMAGE_SCALE*(y+1))
            glEnd()
            # draw_pixel_centre(x,y)
    glFlush()

# note: exits program on mac
def keyboard_original(key, x, y):
    global window_id
    if key == chr(27):
        glutDestroyWindow(window_id)
        if sys.platform == "darwin":
            exit(0)

def render_original():
    global window_id
    glutInit()
    glutInitWindowSize(w * IMAGE_SCALE, h * IMAGE_SCALE)
    window_id = glutCreateWindow('Original Image')
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutDisplayFunc(display_original)
    glutKeyboardFunc(keyboard_original)
    init_original()
    glutMainLoop()

def display_voronoi():
    global im
    w, h = im.size
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    for x in xrange(w):
        for y in xrange(h):
            n = get_node(x, y, im)
            r, g, b = n.rgb
            glColor3ub(r, g, b)
            # glBegin(GL_POLYGON)
            glBegin(GL_LINE_LOOP)
            for pt in n.vor_pts:
                x_pt, y_pt = pt
                y_pt = h - y_pt
                glVertex2f(IMAGE_SCALE*x_pt, IMAGE_SCALE*y_pt)
            glEnd()
            draw_pixel_centre(x, h - y - 1)
    glFlush()

def render_voronoi():
    global window_id, im
    w, h = im.size
    glutInit()
    glutInitWindowSize(w * IMAGE_SCALE, h * IMAGE_SCALE)
    window_id = glutCreateWindow('Voronoi Image')
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutDisplayFunc(display_voronoi)
    glutKeyboardFunc(keyboard_original)
    init_original()
    glutMainLoop()

def render_b_splines():
    pass

def render_b_splines_optimized():
    pass