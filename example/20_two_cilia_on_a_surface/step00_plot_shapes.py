import numpy as np
import os
from machemer import num_phases, shapes_data_path


def get_colors(num, cmap):
    '''
    :param num: How many colors to return
    :param cmap: e.g. 'jet' 'viridis' 'RdBu_r' 'hsv'
    :return:
    '''
    import matplotlib.cm as mcm
    cm = getattr(mcm, cmap)
    return cm(np.linspace(0, 1, num))

x = np.loadtxt(os.path.join(shapes_data_path, 'x-data'))
y = np.loadtxt(os.path.join(shapes_data_path, 'y-data'))
z = np.loadtxt(os.path.join(shapes_data_path, 'z-data'))
c = get_colors(num_phases, 'hsv') # colors

# Plot3D!
# with quick.Plot(projection='3d') as qp:

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d  # 3d visualization

ax = plt.axes(projection='3d')
# ax.set_aspect(1, 'datalim')
for xx, yy, zz, cc in zip(x, y, z, c):
    ax.plot(xx, yy, zz, color=cc, lw=3)

plt.show()
