# find the convex hull of a bunch of points represented as 2-tuples
# using andrew's monotone chain algorithm
# http://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain
# does not remove collinear points if we convert <= to <
def convex_hull(points, keep_collinear=True):
    points = sorted(set(points))
 
    if len(points) <= 1:
        return points
 
    def cross(o, a, b):
        return - (a[0] - o[0]) * (b[1] - o[1]) + (a[1] - o[1]) * (b[0] - o[0])
 
    # Build lower hull
    lower = []
    for p in points:
        if keep_collinear:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) < 0:
                lower.pop()
        else:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
        lower.append(p)
 
    # Build upper hull
    upper = []
    for p in reversed(points):
        if keep_collinear:
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) < 0:
                upper.pop()
        else:
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
        upper.append(p)
 
    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the beginning of the other list. 
    return lower[:-1] + upper[:-1]

# find the convex hull of a bunch of points represented as 2-tuples
# we use the Jarvis march: http://en.wikipedia.org/wiki/Gift_wrapping_algorithm
# may remove collinear points, not used here
def jarvis_march(pts):
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
# note: the PIL system is left-handed, so the > must be replaced by a <
# OpenGL on the other hand is right-handed
def is_to_the_left(a, b, c):
    bc = (c[0] - b[0], c[1] - b[1]) # vector from b to c
    ca = (a[0] - c[0], a[1] - c[1]) # vector from c to a
    return bc[0]*ca[1] - bc[1]*ca[0] < 0

# 'pix' is a pixel with coordinates (x, y)
# where 0 <= x < w * scale
#   and 0 <= y < h * scale
#   and w = width of the input image
#   and h = height of the input image
#   and scale = upscaling factor
# this function returns true if the pixel 'pix'
# is inside 'cvh', which is a convex hull
def is_inside(pix, cvh, scale):
    # simple hack:
    # 1. downscale pix
    # 2. append it to the collinear-triple-less convex hull of n
    #    (assume this is precomputed)
    # 3. compute the convex hull of this new list
    # 4. return is_it_the_same_as_before
    pts = [i for i in cvh] # deep copy of n.vor_pts
    old = set(remove_all_collinear(pts))
    new_pt = (float(pix[0])/scale, float(pix[1])/scale)
    pts.append(new_pt)
    new = set(convex_hull(pts, False))
    return new == old

# returns true if point objects p1 p2 and p3 are collinear
def is_straight_line(p1, p2, p3):
    a, b, c = p1.get_xy(), p2.get_xy(), p3.get_xy()
    return is_straight_line_tuples(a, b, c)

# returns true if tuples a b and c are collinear
def is_straight_line_tuples(a, b, c):
    if a[1] == b[1]: return b[1] == c[1]
    if c[1] == b[1]: return b[1] == a[1]
    slope1 = float(a[0]-b[0]) / float(a[1]-b[1])
    slope2 = float(c[0]-b[0]) / float(c[1]-b[1])
    return slope1 == slope2

# given a convex hull, returns a new convex hull without any collinear points
def remove_all_collinear(pts):
    length = len(pts)
    to_remove = set()
    for i in xrange(len(pts)):
        pt1 = pts[i]
        pt2 = pts[(i+1) % length]
        pt3 = pts[(i+2) % length]
        if is_straight_line_tuples(pt1, pt2, pt3) and pt2 not in to_remove:
            to_remove.add(pt2)
    return [pt for pt in pts if pt not in to_remove]

def test_is_inside():
    c = convex_hull([(0,0), (1,0), (1,1), (1,-1), (2,0), (2,1)])
    assert is_inside((3.8, 2.2), c, 2) is False
    assert is_inside((1.9, 1.1), c, 1) is False
    assert is_inside((1, 1.1), c, 1) is False
    c = convex_hull([(15.75, 10.25), (16.0, 11.0), (17.0, 11.0), (16.75, 10.25), (16.25, 9.75)])
    assert is_inside((67, 40), c, 4) is False

if __name__ == '__main__':
    test_is_inside()