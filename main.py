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
        # ALL voronoi cell points
        # we take the convex hull of these to get
        # the actual voronoi cell points
        self.vor_pts = []

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
w, h = im.size

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
        nodes.append(n)

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
    # print node1.get_xy(), node2.get_xy(),
    assert node1 in node2.neighbours
    assert node2 in node1.neighbours
    curve_len = int(half_curve_len(node1, node2) + half_curve_len(node2, node1) + 1)
    # print curve_len
    return curve_len

# node1 is the node we start exploring from
# node2 is the other node
def half_curve_len(node1, node2):
    assert node1 in node2.neighbours
    assert node2 in node1.neighbours
    # early exit - node1 does not have valence 2
    # so no point exploring further
    if len(node1.neighbours) != 2:
        return 0
    assert len(node1.neighbours) == 2
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
        # print current.get_xy(),
        if current not in encountered:
            encountered.add(current)
        else:
            # cycle detected, divide by half to avoid double-counting
            result /= 2.0
            break
    return result

def largest_connected_components(topleft, topright, bottomleft, bottomright, window_edge_len, im):
    w, h = im.size
    half_window_minus_one = window_edge_len/2 - 1
    # any pixel we encounter should not exceed these bounds
    max_x = min(w-1, bottomright.x + half_window_minus_one)
    min_x = max(0,   topleft.x     - half_window_minus_one)
    max_y = min(h-1, bottomleft.y  + half_window_minus_one)
    min_y = max(0,   topleft.y     - half_window_minus_one)
    # use depth-first search
    component1_size = dfs_connected_component_size(topleft, max_x, min_x, max_y, min_y)
    component2_size = dfs_connected_component_size(topright, max_x, min_x, max_y, min_y)
    return component1_size, component2_size

def dfs_connected_component_size(node, max_x, min_x, max_y, min_y):
    encountered = set([node])
    stack = [node]
    while len(stack) > 0:
        current = stack.pop()
        for ne in current.neighbours:
            if ne not in encountered and min_x <= ne.x <= max_x and min_y <= ne.y <= max_y:
                encountered.add(ne)
                stack.append(ne)
    return len(encountered)

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

        # we increase this each time a heuristic votes to keep diagonal 1
        # and decrease this each time a heuristic votes to keep diagonal 2
        keep_diag1 = 0.0
        # at the end of the three heuristics, if it is > 0, we keep diagonal 2
        # and if it is < 0, we keep diagonal 2
        # no clue what we should do if it equals 0, though

        if fully_connected:
            n.remove_conn(rightdown)
            right.remove_conn(down)

        if only_diagonals:
            # curves heuristic
            # the longer curve should be kept
            diag1_curve_len = overall_curve_len(n, rightdown)
            diag2_curve_len = overall_curve_len(right, down)
            curve_len_difference = abs(diag1_curve_len - diag2_curve_len)
            if diag1_curve_len > diag2_curve_len:
                keep_diag1 += curve_len_difference
            else:
                keep_diag1 -= curve_len_difference
            # sparse pixels heuristic
            # for each diagonal, find the length of the largest connected component
            # while making sure that we stay within a window of, say, 8
            window_edge_len = 8
            component1_size, component2_size = largest_connected_components(n, right, down, rightdown, window_edge_len, im)
            component_size_difference = abs(component1_size - component2_size)
            # if n.get_xy() == (7,10):
            #     print component1_size, component2_size
            if component1_size < component2_size:
                keep_diag1 += component_size_difference
            else:
                keep_diag1 -= component_size_difference
            # islands heuristic
            if (len(n.neighbours) == 1 or len(rightdown.neighbours) == 1) and len(right.neighbours) != 1 and len(down.neighbours) != 1:
                keep_diag1 += 5
            elif len(n.neighbours) != 1 and len(rightdown.neighbours) != 1 and (len(right.neighbours) == 1 or len(down.neighbours) == 1):
                keep_diag1 -= 5

def find_all_voronoi_points(x, y, im):
    n = get_node(x, y, im)

    # for each of the eight directions, decide
    # where to put points, if at all
    # first, the up, down, left, right edges
    up = get_node(x, y-1, im)
    if up is not None:
        if up not in n.neighbours:
            n.vor_pts.append((x, y - 0.25))
    else:
        n.vor_pts.append((x, y - 0.5))

    dn = get_node(x, y+1, im)
    if dn is not None:
        if dn not in n.neighbours:
            n.vor_pts.append((x, y + 0.25))
    else:
        n.vor_pts.append((x, y + 0.5))

    lt = get_node(x, y-1, im)
    if lt is not None:
        if lt not in n.neighbours:
            n.vor_pts.append((x - 0.25, y))
    else:
        n.vor_pts.append((x - 0.5, y))

    rt = get_node(x, y-1, im)
    if rt is not None:
        if rt not in n.neighbours:
            n.vor_pts.append((x + 0.25, y))
    else:
        n.vor_pts.append((x + 0.5, y))

    # next, the diagonal neighbours
    up_in_neighbours = up is not None and up in n.neighbours
    dn_in_neighbours = dn is not None and dn in n.neighbours
    lt_in_neighbours = lt is not None and lt in n.neighbours
    rt_in_neighbours = rt is not None and rt in n.neighbours

    uplt = get_node(x-1, y-1, im)
    if uplt is not None:
        if uplt in n.neighbours:
            n.vor_pts.append((x - 0.5, y - 0.5))
            if up_in_neighbours and not lt_in_neighbours:
                n.vor_pts.append((x - 0.75, y - 0.25))
            elif lt_in_neighbours and not up_in_neighbours:
                n.vor_pts.append((x - 0.25, y - 0.75))
            else:
                n.vor_pts.append((x - 0.75, y - 0.25))
                n.vor_pts.append((x - 0.25, y - 0.75))
        else:
            if up in lt.neighbours:
                # assert lt in up.neighbours
                n.vor_pts.append((x - 0.25, y - 0.25))
            else:
                n.vor_pts.append((x - 0.5, y - 0.5))
    else:
        n.vor_pts.append((x - 0.5, y - 0.5))

    dnlt = get_node(x+1, y-1, im)
    if dnlt is not None:
        if dnlt in n.neighbours:
            if dn_in_neighbours and not lt_in_neighbours:
                n.vor_pts.append((x - 0.75, y + 0.25))
            elif lt_in_neighbours and not dn_in_neighbours:
                n.vor_pts.append((x - 0.25, y + 0.75))
            else:
                n.vor_pts.append((x - 0.75, y + 0.25))
                n.vor_pts.append((x - 0.25, y + 0.75))
        else:
            if dn in lt.neighbours:
                n.vor_pts.append((x - 0.25, y + 0.25))
            else:
                n.vor_pts.append((x - 0.5, y + 0.5))
    else:
        n.vor_pts.append((x - 0.5, y + 0.5))

    uprt = get_node(x-1, y-1, im)
    if uprt is not None:
        if uprt in n.neighbours:
            if up_in_neighbours and not rt_in_neighbours:
                n.vor_pts.append((x + 0.75, y - 0.25))
            elif rt_in_neighbours and not up_in_neighbours:
                n.vor_pts.append((x + 0.25, y - 0.75))
            else:
                n.vor_pts.append((x + 0.75, y - 0.25))
                n.vor_pts.append((x + 0.25, y - 0.75))
        else:
            if up in rt.neighbours:
                n.vor_pts.append((x + 0.25, y + 0.25))
            else:
                n.vor_pts.append((x + 0.5, y + 0.5))
    else:
        n.vor_pts.append((x + 0.5, y - 0.5))

    dnrt = get_node(x-1, y-1, im)
    if dnrt is not None:
        if dnrt in n.neighbours:
            if dn_in_neighbours and not rt_in_neighbours:
                n.vor_pts.append((x + 0.75, y + 0.25))
            elif rt_in_neighbours and not dn_in_neighbours:
                n.vor_pts.append((x + 0.25, y + 0.75))
            else:
                n.vor_pts.append((x + 0.75, y + 0.25))
                n.vor_pts.append((x + 0.25, y + 0.75))
        else:
            if dn in rt.neighbours:
                n.vor_pts.append((x + 0.25, y + 0.25))
            else:
                n.vor_pts.append((x + 0.5, y + 0.5))
    else:
        n.vor_pts.append((x + 0.5, y + 0.5))

# find the convex hull of a bunch of points represented as 2-tuples
# we use the Jarvis march: http://en.wikipedia.org/wiki/Gift_wrapping_algorithm
def convex_hull(pts):
    if len(pts) == 0:
        return []

    result = []

    # first, find the leftmost point
    point_on_hull = sorted(pts, key=lambda x: x[0])[0]

    endpoint = None
    # note: python copies tuples. no need to worry about references here
    while True:
        result.append(point_on_hull)
        endpoint = pts[0]
        for j in xrange(1, len(pts)):
            if endpoint == point_on_hull or is_to_the_left(pts[j], result[-1], endpoint):
                endpoint = pts[j]
        point_on_hull = endpoint
        if endpoint == result[0]:
            break

    return result

# is a to the left of the line from b to c as seen from b?
# http://kukuruku.co/hub/algorithms/a-point-localization-in-a-polygon
def is_to_the_left(a, b, c):
    bc = (c[0] - b[0], c[1] - b[1]) # vector from b to c
    ca = (a[0] - c[0], a[1] - c[1]) # vector from c to a
    return bc[0]*ca[1] - bc[1]*ca[0] > 0

'''tests'''
def test_is_to_the_left():
    assert is_to_the_left((-1,1), (0,0), (1,1)) is True
    assert is_to_the_left((0,0), (0,0), (1,1)) is False
    assert is_to_the_left((2,2), (0,0), (1,1)) is False
    assert is_to_the_left((-0.6,-0.4), (0,0), (1,1)) is True

def test_convex_hull():
    pts1 = [(0,0), (0.5,0.25), (0.75,0.25), (1,0), (0.75,0.75), (0.5,0.75), (0,1), (0.25,0.5)]
    cvh1 = {(0, 1), (0.75, 0.75), (1, 0), (0, 0)}
    assert set(convex_hull(pts1)) == cvh1

test_is_to_the_left()
test_convex_hull()

# similarity graph is now planar
# now construct the simplified voronoi diagram
for x in xrange(w):
    for y in xrange(h):
        find_all_voronoi_points(x, y, im)
        n = get_node(x, y, im)
        n.vor_pts = convex_hull(n.vor_pts)