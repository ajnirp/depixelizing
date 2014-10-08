# usage: python main.py imagefile
# e.g. python main.py img/smw2_yoshi_01.png

import sys
import Image

class Node(object):
    def __init__(self, image, x, y, rgb):
        self.image = image
        self.x = x
        self.y = y
        self.neighbours = set([])
        self.rgb = rgb

    # connect two nodes
    def make_conn(self, n):
        if n is not None:
            self.neighbours.add(n)
            n.neighbours.add(self)

    def remove_conn(self, n):
        if n is not None:
            self.neighbours.remove(n)
            n.neighbours.remove(self)

    def get_xy(self):
        return (self.x, self.y)

imagename = 'img/smw_boo.png'

im = Image.open(imagename)
# im = Image.open(sys.argv[1])
w, h = im.size
# print im.size, im.mode

nodes = []

# im = image object
def get_node(x, y, im):
    w, h = im.size
    if x < 0 or y < 0 or x >= w or y >= h:
        return None
    index = x + y * w
    return nodes[index]

# create nodes
for row in xrange(h):
    for col in xrange(w):
        n = Node(image=im, x=col, y=row, rgb=im.getpixel((col, row)))
        # r, g, b = im.getpixel((col,row))
        # print b,
        nodes.append(n)
    # print

# initialize similarity graph
for row in xrange(h):
    for col in xrange(w):
        n = get_node(col, row, im)
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                if x != 0 or y != 0:
                    neighbour = get_node(col+x, row+y, im)
                    n.make_conn(neighbour)

'''tests'''

def node_corresponds_to_image(im):
    for x in xrange(col):
        for y in xrange(row):
            assert get_node(x,y,im).rgb == im.getpixel((x,y))

def neighbours_are_mutual(im):
    for x in xrange(col):
        for y in xrange(row):
            n = get_node(x,y,im)
            for ne in n.neighbours:
                assert n in ne.neighbours

def number_of_neighbours_is_correct(im):
    w, h = im.size
    # corner nodes have 3 neighbours
    assert len(get_node(0,   0,   im).neighbours) == 3
    assert len(get_node(w-1, 0,   im).neighbours) == 3
    assert len(get_node(0,   h-1, im).neighbours) == 3
    assert len(get_node(w-1, h-1, im).neighbours) == 3
    # border nodes have 5 neighbours
    for x in xrange(1, w-1):
        assert len(get_node(x, 0,   im).neighbours) == 5
        assert len(get_node(x, h-1, im).neighbours) == 5
    for y in xrange(1, h-1):
        assert len(get_node(0,   y, im).neighbours) == 5
        assert len(get_node(w-1, y, im).neighbours) == 5
    # interior nodes have 8 neighbours
    for x in xrange(1, w-1):
        for y in xrange(1, h-1):
            assert len(get_node(x, y, im).neighbours) == 8

'''run tests'''

node_corresponds_to_image(im)
number_of_neighbours_is_correct(im)
neighbours_are_mutual(im)

'''tests over'''

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

# remove dissimilar edges by yuv metric
for x in xrange(w):
    for y in xrange(h):
        n = get_node(x, y, im)
        neighbours_to_remove = [ne for ne in n.neighbours if pixels_are_dissimilar(n.rgb, ne.rgb)]
        for ne in neighbours_to_remove:
            n.remove_conn(ne)

# to measure the curve length that a diagonal is part of
# start from one end of the diagonal and move away from its neighbour in the other direction
# measure the length of that curve. similarly, measure the length of the other curve
# then add the two half-curve lengths (plus 1) to get the length of the entire curve
def overall_curve_len(node1, node2):
    print node1.get_xy(), node2.get_xy(),
    assert(node1 in node2.neighbours)
    assert(node2 in node1.neighbours)
    curve_len = int(half_curve_len(node1, node2) + half_curve_len(node2, node1) + 1)
    print curve_len
    return curve_len

# node1 is the node we start exploring from
# node2 is the other node
def half_curve_len(node1, node2):
    assert(node1 in node2.neighbours)
    assert(node2 in node1.neighbours)
    # early exit - node1 does not have valence 2
    # so no point exploring further
    if len(node1.neighbours) != 2:
        return 0
    assert(len(node1.neighbours) == 2)
    current, previous = node1, node2
    # we store the nodes encountered thus far to detect cycles
    # otherwise, we would loop forever if we enter a cycle
    encountered = set([node2])
    result = 0
    while len(current.neighbours) == 2:
        # get the neighbours of the current pixel
        neighb1, neighb2 = current.neighbours
        # and update current and previous
        old_current_x, old_current_y = current.get_xy()
        if neighb1 == previous:
            current = neighb2
        else:
            current = neighb1
        previous = get_node(old_current_x, old_current_y, im)
        result += 1
        print current.get_xy(),
        if current not in encountered:
            encountered.add(current)
        else:
            # cycle detected, divide by half to avoid double-counting
            result /= 2.0
            break
    return result

# apply heuristics to make graph planar
for x in xrange(w-1):
    for y in xrange(h-1):
        n = get_node(x, y, im)
        right = get_node(x+1, y, im) # node to the right of the curr node
        down = get_node(x, y+1, im) # node directly below the curr node
        rightdown = get_node(x+1, y+1, im) # node directly below and to the right of the curr node

        # edges
        self_to_right = right in n.neighbours
        self_to_down = down in n.neighbours
        right_to_rightdown = right in rightdown.neighbours
        down_to_rightdown = down in rightdown.neighbours
        # diagonals
        diag1 = rightdown in n.neighbours
        diag2 = down in right.neighbours

        # check if fully connected
        vert_and_horiz_edges = self_to_right and self_to_down and right_to_rightdown and down_to_rightdown
        no_vert_horiz_edges = not (self_to_right or self_to_down or right_to_rightdown or down_to_rightdown)
        both_diagonals = diag1 and diag2

        fully_connected = vert_and_horiz_edges and both_diagonals # all 6 connections are present
        only_diagonals = no_vert_horiz_edges and both_diagonals # only the diagonals are present

        if fully_connected:
            n.remove_conn(rightdown)
            right.remove_conn(down)

        if only_diagonals:
            # curves heuristic
            overall_curve_len(n, rightdown)
            overall_curve_len(right, down)
            pass