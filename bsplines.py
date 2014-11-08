# credit - this code is a modified version of http://stackoverflow.com/a/24693358

from numpy import array, linspace
import matplotlib.pyplot as plt
import scipy.interpolate as si

def bspline(pts, degree, smoothness):
    # cycle check
    periodic = False
    if pts[0] == pts[-1]:
        # pts.pop()
        periodic = True
        pts = pts[:-1]

    if periodic: pts = pts + pts[0 : degree+1]
    else: pts = [pts[0]] + pts + [pts[-1],pts[-1]]

    pts = array(pts)
    n_points = len(pts)
    x, y = pts[:,0], pts[:,1]

    t = range(len(x))
    ipl_t = linspace(1.0, len(pts) - degree, smoothness)

    x_tup = si.splrep(t, x, k=degree, per=periodic)
    y_tup = si.splrep(t, y, k=degree, per=periodic)
    x_list = list(x_tup)
    xl = x.tolist()

    y_list = list(y_tup)
    yl = y.tolist()

    if periodic:
        x_list[1] = [0.0] + xl + [0.0, 0.0, 0.0, 0.0]
        y_list[1] = [0.0] + yl + [0.0, 0.0, 0.0, 0.0]

    x_i = si.splev(ipl_t, x_list)
    y_i = si.splev(ipl_t, y_list)

    return zip(x_i, y_i)