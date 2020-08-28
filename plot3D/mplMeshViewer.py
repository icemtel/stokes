"""
Visualize mesh with matplotlib
"""

import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d  # 3d visualization
import FBEM


def triangular_mesh_from_array(points_array, trias_array, ax=None, **kwargs):
    '''
    representation: 'surface', 'wireframe', 'points', 'mesh', 'fancymesh'
    :param points_array: sp.array([[x11,x12,x12],[x21,..]])
    :param trias_array: sp.array([tria1, tria2,..]), where tria contains ids of triangle points;
           Numeration starts from 1 (Double-check); e.g. tria = [1, 101, 50]

    :return:
    '''
    if ax is None:
        ax = plt.gca()
    ax.plot_trisurf(points_array[:, 0], points_array[:, 1], points_array[:, 2],
                    triangles=trias_array, **kwargs)

    return ax


class MeshViewer:
    '''
    General class with support of quiver, etc
    '''

    def __init__(self, path, group='.'):
        self.source = FBEM.Source(path, group)
        self.fig = None
        self.ax = None

    def create_ax(self):
        self.fig = plt.figure(figsize=plt.figaspect(0.5) * 1.5)  # reduces scale disproportion between axes
        self.ax = plt.axes(projection='3d')


    def triangular_mesh(self, names='all', **kwargs):
        '''
        :param names: name or list of name of objects to visualize
        :param kwargs: keyword arguments to pass to the plt.plot_trisurf
        '''
        if isinstance(names, str):
            names = [names]
        nodes_list, trias_list = self.source.read_triangulation_list(names)
        for nodes, trias in zip(nodes_list, trias_list):
            triangular_mesh_from_array(nodes, trias, ax=self.ax, **kwargs)


    def show(self, set_aspect=True):
        if set_aspect: # small hack since there's no matplotlib function which would set equal aspect ratio in 3d
            scaling = np.array([getattr(self.ax, 'get_{}lim'.format(dim))() for dim in 'xyz']);
            self.ax.auto_scale_xyz(*[[np.min(scaling), np.max(scaling)]] * 3)
        plt.show()


def _average_values(vals, weights=None, n=1, indices_to_skip=None):
    '''
    - Take average of groups of every n elements.
        - If there are less than n elements in the tail, take the average of those and append to the result anyway.
    - Skip elements which indices are given in `indices_to_skip`.
    - Return a list of averaged values.
    - Values can be n-dimensional.
    '''

    # Modify indices_to_skip; replacing negative values with positive, to be correctly compared with idx
    def chunks(l, n):
        """
        Yield successive n-sized chunks from l.
        Last chunk will be smaller and will contain the rest of the elements
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]

    if weights is None:
        weights = np.ones(vals.shape[0])

    if indices_to_skip is not None:
        indices_to_skip_array = np.array(indices_to_skip)
        indices_to_skip_array = np.where(indices_to_skip_array >= 0, indices_to_skip_array,
                                         indices_to_skip_array + len(vals))
        vals = np.delete(vals, indices_to_skip_array, axis=0)  # Skip values

    vals_new = []
    for vals_chunk, weights_chunk in zip(chunks(vals, n), chunks(weights, n)):
        val_new = np.average(vals_chunk, axis=0, weights=weights_chunk)
        vals_new.append(val_new)

    return np.array(vals_new)