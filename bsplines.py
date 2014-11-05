import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as si

points = [[-2, 2], [0, 1], [-2, 0], [0, -1], [-2, -2], [-4, -4], [2, -4], [4, 0], [2, 4], [-4, 4]]

degree = 3 # "breaks" the loop

points = points + points[0:degree + 1]
points = np.array(points)
n_points = len(points)
x = points[:,0]
y = points[:,1]

t = range(len(x))
ipl_t = np.linspace(1.0, len(points) - degree, 1000)

x_tup = si.splrep(t, x, k=degree, per=1)
y_tup = si.splrep(t, y, k=degree, per=1)
x_list = list(x_tup)
xl = x.tolist()
x_list[1] = [0.0] + xl + [0.0, 0.0, 0.0, 0.0]

y_list = list(y_tup)
yl = y.tolist()
y_list[1] = [0.0] + yl + [0.0, 0.0, 0.0, 0.0]

x_i = si.splev(ipl_t, x_list)
y_i = si.splev(ipl_t, y_list)

plt.plot(x, y, '-og')
plt.plot(x_i, y_i, 'r')
plt.show()