import math, random

from OpenGL.GL import *
from OpenGL.GLUT.freeglut import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from hull import *

def process_keyboard_input(key, x, y):
    global window_id
    if key == chr(27):
        glutLeaveMainLoop()

def init_scene(w, h, scale):
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glColor3f(0.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, scale*w, 0, scale*h)
    glPointSize(3)

def set_random_color():
    glColor3ub(random.randint(0,255), random.randint(0,255), random.randint(0,255))

def draw_pixel_centres(w, h, im, nodes, scale):
    for x in xrange(w):
        for y in xrange(h):
            draw_pixel_centre(x, h-y-1, im, nodes, scale)

def draw_pixel_centre(x, y, im, nodes, scale):
    _, h = im.size
    r, g, b = get_node(x, h-y-1, im, nodes).rgb
    glColor3ub(r, g, b)
    perturb = 0.075

    pts = [(scale*(x+0.5-perturb), scale*(y+0.5-perturb)),
            (scale*(x+0.5-perturb), scale*(y+0.5+perturb)),
            (scale*(x+0.5+perturb), scale*(y+0.5+perturb)),
            (scale*(x+0.5+perturb), scale*(y+0.5-perturb))]

    # fill
    glBegin(GL_POLYGON)
    for x, y in pts:
        glVertex2f(x, y)
    glEnd()

    # stroke
    glColor3ub(255-r, 255-g, 255-b)
    glBegin(GL_LINE_LOOP)
    for x, y in pts:
        glVertex2f(x, y)
    glEnd()

def get_node(x, y, im, nodes):
    w, h = im.size
    if x < 0 or y < 0 or x >= w or y >= h:
        return None
    index = x + y * w
    return nodes[index]

# convert rgb to yuv
def rgb2yuv(r,g,b):
    r1 = r / 255.0
    g1 = g / 255.0
    b1 = b / 255.0
    y = (0.299 * r1) + (0.587 * g1) + (0.114 * b1)
    u = 0.492 * (b1 - y)
    v = 0.877 * (r1 - y)
    return (y, u, v)

# compare YUV values of two pixels, return
# True if they are different, else False
def pixels_are_dissimilar(rgb1, rgb2):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    y1, u1, v1 = rgb2yuv(r1, g1, b1)
    y2, u2, v2 = rgb2yuv(r2, g2, b2)
    ydiff = abs(y1 - y2) > 48.0/255
    udiff = abs(u1 - u2) > 7.0/255
    vdiff = abs(v1 - v2) > 6.0/255
    return ydiff or udiff or vdiff

def is_shading_edge(rgb1, rgb2):
    y1, u1, v1 = rgb2yuv(*rgb1)
    y2, u2, v2 = rgb2yuv(*rgb2)
    dist = (y1 - y2)**2 +(u1 - u2)**2 + (v1 - v2)**2
    return (dist <= (float(100)/255)**2)

def is_contour_edge(pt1, pt2):
    intersection = pt1.nodes & pt2.nodes
    if len(intersection) == 1:
        return True
    else:
        node1, node2 = intersection
        return not is_shading_edge(node1.rgb, node2.rgb)

def angle(o, a, b):
    def d(l, m): return (l.x - m.x)**2 + (l.y - m.y)**2
    P12, P23, P13 = d(o, a), d(a, b), d(o, b)
    angle = math.acos((P12 + P13 - P23) / (2 * math.sqrt(P12 * P13)))
    return math.degrees(angle) # converted from radians

# pt1 and pt2 are two polygon vertices in the simplified voronoi
# diagram this function checks if the reshaped pixels corresponding
# to the two polygons on either side of the edge joining pt1 to pt2
# are different enough for the edge to be classified as visible
def polygons_are_dissimilar(pt1, pt2):
    # get the pixels associated with both points and take the intersection of the two sets
    # this either has size 2 or size 1
    # the second case happens when the two polygon points are on the boundary
    # in this case, the edge is trivially not a visible edge since there is no
    # need to draw b-splines along the boundary
    # note that here, by "visible edge" we mean a single-length visible edge
    # whereas elsewhere, we use it to mean "a sequence of nodes separating 2 regions"
    intersection = pt1.nodes & pt2.nodes
    if len(intersection) == 1:
        return True
    else:
        assert len(intersection) == 2
        node1, node2 = intersection
        return pixels_are_dissimilar(node1.rgb, node2.rgb)

def process_command_line_arg(argname, necessary=False, needs_arg=True, missing_error=''):
    # print argname, needs_arg
    if argname not in sys.argv:
        if necessary:
            sys.stderr.write(missing_error + '\n')
            exit(1)
        else:
            return None
    index = sys.argv.index(argname)
    if needs_arg:
        if len(sys.argv) < index + 2:
            sys.stderr.write(argname + ' needs an argument\n')
            exit(1)
        else:
            return sys.argv[index+1]
    else:
        return True

def color_pixels_bsplines(im ,scale, nodes):
    w, h = im.size
    count = 0
    # glBegin(GL_POINTS)
    for x in xrange(w*scale):
        for y in xrange(h*scale):
            n = get_node(x//scale, y//scale, im, nodes)
            # who does this pixel belong to?
            candidates = [ne for ne in n.neighbours]
            candidates.append(n)
            result = None
            for node in candidates:
                if is_inside((x, y), node.vor_pts, scale):
                    result = node
                    break
            if result is None:
                print (x, y), [c.vor_pts for c in candidates]
                count += 1
            # continue
            # node_x, node_y = result.get_xy()
            # r, g, b = get_node(node_x, node_y, im, nodes).rgb
            # glColor3ub(r, g, b)
            # glVertex2f(x, h-y)
    print count
    # glEnd()