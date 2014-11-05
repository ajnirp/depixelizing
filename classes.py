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

    def print_neighbours(self):
        print [ne.get_xy() for ne in self.neighbours]

    def __eq__(self, other):
        return self.get_xy() == other.get_xy()

    def __repr__(self):
        return str(self.get_xy())

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # nodes whose voronoi cells contain this point as a vertex
        # in other words, the set of nodes that 'own' this point
        self.nodes = set([])
        # visible edges that this point is a part of
        self.vedges = set([])
        # neighbouring points dict
        # this maps an owner node to the set of neighbours the
        # point has with respect to that node
        self.neighbours = {}
        # is the point an endpoint belonging to several vedges?
        # or is it just a point in the middle of a vedge
        self.is_endpoint = False

    def add_node(self, n):
        self.nodes.append(n)

    def add_vedge(self, ve):
        self.vedges.add(ve)

    def get_xy(self):
        return (self.x, self.y)

    def __eq__(self, other):
        return self.get_xy() == other.get_xy()

    def __repr__(self):
        return str(self.get_xy())

    def all_neighbours(self):
        return set.union(*[self.neighbours[n] for n in self.nodes])

class VisibleEdge(object):
    def __init__(self, points=[]):
        # list of points comprising the visible edge
        self.points = points
        self.bspline = None

    def get_endpoints(self):
        return (self.points[0], self.points[-1])