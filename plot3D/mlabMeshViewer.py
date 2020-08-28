"""
mayavi - 3D visualization tool; based on vtk

Rotate camera with mouse; ctrl/shift + mouse also moves camera in a different way

## Set size and background color
fig = mlab.figure(size=(720,720), bgcolor = (0.9, 0.9,0.9))
fig.scene._lift() # to save screenshots in jupyter notebook

view = mlab.view() -> get current camera view parameters

mlab.view(*view) -> set current camera view



"""

import mayavi.mlab as mlab
import numpy as np
from numpy.linalg import norm
import FBEM


def show(func=None, stop=False):
    return mlab.show(func, stop)


def triangular_mesh_from_array(points_array, trias_array, *args, **kwargs):
    '''
    representation: 'surface', 'wireframe', 'points', 'mesh', 'fancymesh'
    :param points_array: sp.array([[x11,x12,x12],[x21,..]])
    :param trias_array: sp.array([tria1, tria2,..]), where tria contains ids of triangle points;
           Numeration starts from 1 (Double-check); e.g. tria = [1, 101, 50]

    :return:
    '''
    mlab.triangular_mesh(points_array[:, 0], points_array[:, 1], points_array[:, 2], trias_array,
                         *args, **kwargs)


def quick_mesh_plot(path, group='.'):
    mv = MeshViewer(path, group)
    mv.triangular_mesh()
    mv.show()


class MeshViewer:
    '''
    General class with support of quiver, etc
    '''

    def __init__(self, path, group='.'):
        self.source = FBEM.Source(path, group)

    def triangular_mesh(self, names='all', *args, **kwargs):
        if isinstance(names, str):
            names = [names]
        nodes_list, trias_list = self.source.read_triangulation_list(names)
        for nodes, trias in zip(nodes_list, trias_list):
            triangular_mesh_from_array(nodes, trias, *args, **kwargs)

    def force_density_arrows(self, names='all', points_per_arrow=1, indices_to_skip=None, color=(1, 0, 0),
                             offset_distance=None, inverse_direction=False, scale_factor='auto', mode='arrow', **kwargs):
        '''
        Plot force density.
        See _plot_vector_field for more
        Use offset_distance = radius when plotting on cilia
        Take sum of forces, divide by sum of areas
        (equivalently take averaged sum of force densities; with weights = areas)
        '''
        if inverse_direction:
            sign = -1
        else:
            sign = +1
        if 'line_width' not in kwargs.keys():
            kwargs['line_width'] = 10
        coords_array_list = []
        force_densities_array_list = []
        areas_array_list = []
        if isinstance(names, str):
            names = [names]
        data_list = self.source.read_data_list(names)
        for data in data_list:
            coords = data.coordinates
            areas = data.areas
            force_densities = sign * data.forces / areas[:, np.newaxis]
            coords_array_list.append(coords)
            force_densities_array_list.append(
                force_densities)  # Will be averaged with weights = areas <=> sum[(f * A) / A]/sum[A]
            areas_array_list.append(areas)

        _plot_vector_field(coords_array_list, force_densities_array_list, areas_array_list,
                           points_per_arrow, indices_to_skip,  offset_distance=offset_distance,
                           color=color, scale_factor=scale_factor, mode=mode, **kwargs)

    def velocity_arrows(self, names='all', points_per_arrow=1, indices_to_skip=None, color=(0, 0, 1),
                        offset_distance=None, scale_factor='auto', mode='arrow', **kwargs):
        '''
        Plot velocity field.
        See _plot_vector_field for more
        Use offset_distance = radius when plotting on cilia
        '''
        if 'line_width' not in kwargs.keys():
            kwargs['line_width'] = 10
        coords_array_list = []
        velocities_array_list = []
        if isinstance(names, str):
            names = [names]
        data_list = self.source.read_data_list(names)
        for data in data_list:
            coords = data.coordinates
            velocities = data.velocities
            coords_array_list.append(coords)
            velocities_array_list.append(velocities)

        _plot_vector_field(coords_array_list, velocities_array_list, None, points_per_arrow, indices_to_skip,
                           offset_distance=offset_distance,
                           color=color, scale_factor=scale_factor, mode=mode, **kwargs)

    def show(self):
        show()


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


def _plot_vector_field(coords_array_list, vectors_array_list, weights_array_list=None, points_per_arrow=1,
                       indices_to_skip=None,
                       offset_distance=None, color=(1, 1, 1), scale_factor='auto', mode='arrow', **kwargs):
    '''
    Arrows will be rescaled together for each object for which the name is given.
    If don't want that - run this function for each object separately.
    :param names: Either name or list of names of objects; e.g. ['flagellum_1']
    :param points_per_arrow: Number of elements to average over
    :param indices_to_skip:
    :param offset_distance: Move arrows from the middle of a cilium; offset_distance = radius in that case.
                            Will not work with other geometrical objects.
    :param scale_factor: set to constant, if want to keep the same arrow size amongst different objects/frames
    :return:
    '''
    if 'line_width' not in kwargs.keys():
        kwargs['line_width'] = 10
    if weights_array_list is None:
        weights_array_list = [None for _ in coords_array_list]  # To match dimensions
    coords_avg_array_list = []
    vectors_avg_array_list = []
    for coords, vectors, weights in zip(coords_array_list, vectors_array_list, weights_array_list):
        coords_avg = np.array(_average_values(coords, n=points_per_arrow, indices_to_skip=indices_to_skip))
        vectors_avg = np.array(_average_values(vectors, weights, n=points_per_arrow, indices_to_skip=indices_to_skip))

        ## Move arrows to the flagellum surface
        drr = np.diff(coords_avg, axis=0, prepend=[coords_avg[1] - coords_avg[0]])
        drr_norm = drr / norm(drr, axis=-1)[:, np.newaxis]
        if offset_distance is not None:
            # Move the start of arrows in the direction of the force; but substract the part; which is parallel to the dr
            offset_direction = (vectors_avg - drr_norm * np.sum(drr_norm * vectors_avg, axis=-1)[:, np.newaxis])
            offset_direction /= norm(offset_direction, axis=-1)[:, np.newaxis]  # Normalize
            offset = offset_distance * offset_direction
            coords_avg += offset

        coords_avg_array_list.append(coords_avg)
        vectors_avg_array_list.append(vectors_avg)

    coords_new = np.concatenate(coords_avg_array_list)
    vectors_new = np.concatenate(vectors_avg_array_list)
    ## Plot
    x, y, z = coords_new.T
    u, v, w = vectors_new.T
    mlab.quiver3d(x, y, z, u, v, w, color=color, scale_factor=scale_factor, mode=mode, **kwargs)
