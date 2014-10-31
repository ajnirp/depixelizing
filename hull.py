# find the convex hull of a bunch of points represented as 2-tuples
# using andrew's monotone chain algorithm
# http://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain
# does not remove collinear points if we convert <= to <
def convex_hull(points):
    points = sorted(set(points))
 
    if len(points) <= 1:
        return points
 
    def cross(o, a, b):
        return - (a[0] - o[0]) * (b[1] - o[1]) + (a[1] - o[1]) * (b[0] - o[0])
 
    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) < 0:
            lower.pop()
        lower.append(p)
 
    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) < 0:
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