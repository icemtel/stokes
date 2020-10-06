'''
To add/improve:
- objects are solid color or trimesh
- exclude large arrows in vicinity of singularity
'''
import numpy as np
import FBEM
import matplotlib.pyplot as plt


def _get_keys(projection):
    if projection == 'xy':
        keyX = 0
        keyY = 1
        keyZ = 2
    elif projection == 'xz':
        keyX = 0
        keyY = 2
        keyZ = 1
    elif projection == 'yz':
        keyX = 1
        keyY = 2
        keyZ = 0
    else:
        raise KeyError
    return keyX, keyY, keyZ


def extract_flowfield(source):
    try:
        data = source.read_data()
    except:
        data = FBEM.extract_all_data(source)
    flowfield = data.extract_flowfield()
    return flowfield


def get_flow_vectors_grid(flow, projection, x1s, x2s, x3_offset=0):
    '''
    Evaluate flowfield on the grid of (x1,x2) from x1s, x2s
    '''
    keyX1, keyX2, keyX3 = _get_keys(projection)
    f1 = np.zeros((len(x2s), len(x1s)))
    f2 = np.zeros((len(x2s), len(x1s)))
    f3 = np.zeros((len(x2s), len(x1s)))
    coord = np.zeros(3)  # to be filled
    for ix2, x2 in enumerate(x2s):
        for ix1, x1 in enumerate(x1s):
            # get coordinate
            coord[keyX1] = x1
            coord[keyX2] = x2
            coord[keyX3] = x3_offset
            flowXYZ = flow(coord)
            f1[ix2, ix1] = flowXYZ[keyX1]
            f2[ix2, ix1] = flowXYZ[keyX2]
            f3[ix2, ix1] = flowXYZ[keyX3]
    return f1, f2, f3


def create_grid(xrange, grid):
    xs, dx = np.linspace(*xrange, grid, endpoint=False, retstep=True)
    xs += dx / 2  # centralize
    return xs


def plot_flowfield_color(flowfield, projection, x1range, x2range, x3_offset=0, grid=20,
                         ax=None, norm=None, cmap='viridis', colorbar=True, **kwargs):
    '''
    Plot flow field.
    :param source: FBEM source class, or folder name
    :param projection: 'xy', 'xz', 'yz'
    :param x1_range, x2_range: plot limits
    :param x3_offset: plot in plane, which does not go through zero
    :param ax: matplotlib ax object, optional
    :param norm:
    :param cmap:
    :param colorbar:
    :param grid: use `grid ** 2` sample points
    :param kwargs: passed to imshow
    :return:
    '''

    # if ax exists, plot to the  ax
    if ax == None:
        ax = plt.gca()

    x1s = create_grid(x1range, grid)
    x2s = create_grid(x2range, grid)
    # Extract flow values
    f1, f2, f3 = get_flow_vectors_grid(flowfield, projection, x1s, x2s, x3_offset)
    magnitudes = np.linalg.norm([f1, f2, f3], axis=0)
    # Altenative to imshow - pcolormesh?
    im = ax.imshow(magnitudes, extent=[*x1range, *x2range],
                   origin='lower', norm=norm, cmap=cmap,
                   **kwargs)  # origin lower - to specifiy how this matrix has to be plotted
    # Adjust axes
    ax.set_xlim(x1range)
    ax.set_ylim(x2range)
    ax.set_aspect(1)
    # Set x and y labels on plot, according to 'projection'
    ax.set_xlabel(f"${projection[0]}$")
    ax.set_ylabel(f"${projection[1]}$")
    if colorbar:
        plt.colorbar(im)

    return im


def plot_flowfield_arrows(flowfield, projection, x1range, x2range, x3_offset=0, grid=20,
                          ax=None, arrow_color=(1, 1, 1), **kwargs):
    '''
    :kwargs: passed to quiver
    '''
    # if ax exists, plot to the  ax
    if ax == None:
        ax = plt.gca()

    x1s = create_grid(x1range, grid)
    x2s = create_grid(x2range, grid)
    # Extract flow values
    f1, f2, f3 = get_flow_vectors_grid(flowfield, projection, x1s, x2s, x3_offset)
    qv = ax.quiver(x1s, x2s, f1, f2, color=arrow_color, angles='xy', **kwargs)
    return qv




