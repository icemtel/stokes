"""
Visualzie using `vedo` (a.k.a. `vtkplotter`) package

- I don't define my own MeshViewer class, because vedo.Mesh class is already very functional

# In jupyter:
# vedo.embedWindow(False)
#embedWindow('2d') # for a static image
"""

import vedo
import FBEM
import numpy as np


def get_colors(num, cmap, endpoint=True):
    '''
    :param num: How many colors to return
    :param cmap: e.g. 'jet' 'viridis' 'RdBu_r' 'hsv'
    :return:
    '''
    import matplotlib.cm as mcm
    cm = getattr(mcm, cmap)
    return cm(np.linspace(0, 1, num, endpoint=endpoint))


def get_cilium_colors_rgb(num_phases, cmap='hsv'):
    '''
    Returns colors, coding cilia phases.
    '''
    colors = get_colors(num_phases, cmap, endpoint=False)
    colors = [c[:3] for c in colors]  # only RGB, no alpha
    return colors


def triangulation_to_vedo_mesh(tri, **kwargs):
    """
    Transform my triangulation class to Trimesh class
    :param kwargs:
    """
    coords = tri.coordinates
    trias = tri.triangulation
    m = vedo.Mesh([coords, trias], **kwargs)
    return m


def source_to_vedo_mesh(source, name, **kwargs):
    coords, trias = source.read_triangulation(name)
    m = vedo.Mesh([coords, trias], **kwargs)
    return m


def MeshViewer(path, names=None, colors=None, group='.'):
    """
    Get Trimesh class instance from FBEM results.
    - set colors to each object
    :param path:
    :param group:
    :param names: list of names of objects to plot; or a single name
    :param colors: list of colors - 4-tuples;
                   if not given- use random colors; some entries are None => replace with random colors
    :return:
    """
    source = FBEM.Source(path, group)
    # if names is a single name string
    if isinstance(names, str):
        names = [names]
    # if no names are given - get all names from ranges
    elif names is None:  #
        names = source.read_ranges().get_names()
    # if no colors are given - define a list of matching length
    if colors is None:
        colors = [None for _ in names]

    for i, c in enumerate(colors):
        if c is None:
            color = np.random.rand(3)
            colors[i] = color

    meshes = []
    for color, name in zip(colors, names):
        m = source_to_vedo_mesh(source, name, c=color)
        meshes.append(m)

    m_combined = vedo.assembly.Assembly(meshes)  # vedo.merge(*meshes) # loses individual colors
    return m_combined


def FlagellaPlaneViewer(path, phases, num_phases, group='.', cmap='hsv', plane_color='lightgrey'):
    '''
    Visualize flagella and the plane.
    - Color flagella in accordance with their phase
    - Assume first N objects - cilia/flagella, and N+1th object - plane
    '''
    colors_list = get_cilium_colors_rgb(num_phases, cmap=cmap)
    # Colors to RGB

    flagella_colors = []
    for phase in phases:
        color = colors_list[phase]
        flagella_colors.append(color)

    flagella_names = [f'flagellum_{i + 1}' for i in range(len(phases))]
    flagella_mesh = MeshViewer(path, group=group, colors=flagella_colors, names=flagella_names)

    plane_mesh = MeshViewer(path, group=group, names=['plane'], colors=[plane_color])

    m_combined = flagella_mesh + plane_mesh
    return m_combined


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


# def vector_avg_and_auto_scale(coords, vectors, points_per_arrow, arrow_length_range, indices_to_skip=None):
#     """
#     - Returns list of vectors to display
#     - Reduces number of vectors by taking averages
#     - Rescales vectors s.t. maximum vector length equals to arrow_length_range[1]
#     - Vectors which are shorter than arrow_length_range[0] are removed from the output
#     - returns average coordinates, average vectors (rescaled), and the vector scale (rescaling factor)
#     """
#     # Check:
#     assert len(coords) == len(vectors)
#     min_arrow_length, max_arrow_length = arrow_length_range
#     coords_avg = np.array(_average_values(coords, weights=None, n=points_per_arrow, indices_to_skip=indices_to_skip))
#     vectors_avg = np.array(_average_values(vectors, weights=None, n=points_per_arrow, indices_to_skip=indices_to_skip))
#     # Determine scale
#     magnitude_max = np.linalg.norm(vectors_avg, axis=1).max()
#     scale = max_arrow_length / magnitude_max
#     vectors_avg *= scale  # rescale vectors
#
#     coords_new = []
#     vectors_new = []
#     for c, v in zip(coords_avg, vectors_avg):
#         arrow_length = np.linalg.norm(v)
#         if arrow_length > min_arrow_length:  # do not plot really small arrows
#             coords_new.append(c)
#             vectors_new.append(v)
#
#     return np.array(coords_new), np.array(vectors_new), scale


def vector_avg_and_scale(coords, vectors, points_per_arrow, scale=1., min_arrow_length=0., weights=None,
                         indices_to_skip=None):
    """
    - Returns list of vectors to display
    - Reduces number of vectors by taking averages
    - Rescales vectors by a given number `scale`
    - Vectors which are shorter than `min_arrow_length` are removed from the output
    - returns average coordinates, average vectors (rescaled), and the vector scale (rescaling factor)
    """
    # Check:
    assert len(coords) == len(vectors)
    coords_avg = np.array(_average_values(coords, weights=None, n=points_per_arrow, indices_to_skip=indices_to_skip))
    vectors_avg = np.array(
        _average_values(vectors, weights=weights, n=points_per_arrow, indices_to_skip=indices_to_skip))
    # Scale
    vectors_avg *= scale  # rescale vectors

    coords_new = []
    vectors_new = []
    for c, v in zip(coords_avg, vectors_avg):
        arrow_length = np.linalg.norm(v)
        if arrow_length > min_arrow_length:  # do not plot really small arrows
            coords_new.append(c)
            vectors_new.append(v)

    return np.array(coords_new), np.array(vectors_new)


def VelocityArrows(path, names, points_per_arrow, scale=1.,
                   c='blue', min_arrow_length=0., group='.', **kwargs):
    '''
    Averages arrows over several elements:
    - works correctly only if they are located nearby;
    - Tested only on cilia; works with most recent implementation;
    - Coordinate where the arrow starts is the geometrical center of averaged elements
    - Velocity average is calculated simply as a mean.

    - In more general case: may need some clustering of points
    :param path: path to hydrodynamic computation results
    :param names:
    :param points_per_arrow:
    :param scale: multiply arrow lengths by scale
    :param min_arrow_length: do not plot arrows below this length
    :param group: if inside hdf5 file - hdf5 group
    :param **kwargs: passed to Arrows class
    :return: arrow object and scale
    '''
    source = FBEM.Source(path, group)
    to_plot_list = []
    for name in names:
        data_cilium = source.read_data(name)  # data on the cilium
        # Data
        coords = data_cilium.coordinates
        vels = data_cilium.velocities

        #  Velocity Arrows
        coords_avg, vectors_avg = vector_avg_and_scale(coords, vels, points_per_arrow, scale, min_arrow_length)
        # Create arrows actors
        if len(coords_avg) > 0:
            startPoints = coords_avg
            endPoints = coords_avg + vectors_avg
            print(np.amax(np.linalg.norm(vectors_avg, axis=1)))
            arrows = vedo.shapes.Arrows(startPoints, endPoints, c=c, **kwargs)
            to_plot_list.append(arrows)
    arrows_combined = vedo.assembly.Assembly(to_plot_list)
    return arrows_combined


def ForceArrows(path, names, points_per_arrow, scale=1.,
                c='red', min_arrow_length=0., group='.', **kwargs):
    '''
    Averages arrows over several elements:
    - works correctly only if they are located nearby;
    - Tested only on cilia; works with most recent implementation;
    - Coordinate where the arrow starts is the geometrical center of averaged elements
    - Force average is calculated as sum of forces on some elements; divided by sum of element areas.
      (implemented as `sum[(f * A) / A]/sum[A]`)

    - In more general case: may need some clustering of points

    :param path: path to hydrodynamic computation results
    :param names:
    :param points_per_arrow:
    :param scale: multiply arrow lengths by scale
    :param min_arrow_length: do not plot arrows below this length
    :param group: if inside hdf5 file - hdf5 group
    :param **kwargs: passed to Arrows class
    :return: arrow object and scale
    '''
    source = FBEM.Source(path, group)
    to_plot_list = []
    for name in names:
        data_cilium = source.read_data(name)  # data on the cilium
        # Data
        coords = data_cilium.coordinates
        forces = data_cilium.forces  # f
        areas = data_cilium.areas  # A
        force_densities = forces / areas[:, np.newaxis]  # f * A

        #  Force arrows
        # # Will be averaged with weights = areas <=> sum[(f * A) / A]/sum[A]
        coords_avg, vectors_avg = vector_avg_and_scale(coords, force_densities, weights=areas,
                                                       points_per_arrow=points_per_arrow,scale=scale,
                                                       min_arrow_length=min_arrow_length)

        # Create arrows actors
        if len(coords_avg) > 0:
            startPoints = coords_avg
            endPoints = coords_avg + vectors_avg
            arrows = vedo.shapes.Arrows(startPoints, endPoints, c=c, **kwargs)
            to_plot_list.append(arrows)
    arrows_combined = vedo.assembly.Assembly(to_plot_list)
    return arrows_combined
