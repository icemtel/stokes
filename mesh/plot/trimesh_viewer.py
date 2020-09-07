"""
Visualzie using `trimesh` package

- I don't define my own MeshViewer class, because trimesh.Trimesh class is already very functional
"""

import trimesh
import FBEM
import numpy as np


def get_colors(num, cmap):
    '''
    :param num: How many colors to return
    :param cmap: e.g. 'jet' 'viridis' 'RdBu_r' 'hsv'
    :return:
    '''
    import matplotlib.cm as mcm
    cm = getattr(mcm, cmap)
    return cm(np.linspace(0, 1, num))


def triangulation_to_trimesh(tri):
    """
    Transform my triangulation class to Trimesh class
    """
    coords = tri.coordinates
    trias = tri.triangulation
    m = trimesh.Trimesh(vertices=coords, faces=trias,
                        validate=True)
    return m


def MeshViewer(path, names=None, colors=None, group='.'):
    """
    Get Trimesh class instance from FBEM results.
    - set colors to each object
    :param path:
    :param group:
    :param names: list of names of objects to plot
    :param colors: list of colors - 4-tuples;
                   if not given- use random colors; some entries are None => replace with random colors
    :return:
    """
    source = FBEM.Source(path, group)
    # if no names are given - get all names from ranges
    if names is None:  #
        names = source.read_ranges().get_names()
    # if no colors are given - define a list of matching length
    if colors is None:
        colors = [None for _ in names]
    # replace None's with random colors
    for icolor, color in enumerate(colors):
        if color is None:
            random_color = trimesh.visual.random_color()
            colors[icolor] = random_color

    nodes_list, trias_list = source.read_triangulation_list(names)

    meshes = []
    for nodes, trias in zip(nodes_list, trias_list):
        m = trimesh.Trimesh(vertices=nodes, faces=trias, validate=True)
        meshes.append(m)

    for m, c in zip(meshes, colors):
        m.visual.face_colors = c

    m_combined = sum(meshes)
    return m_combined


def FlagellaPlaneViewer(path, phases, num_phases, group='.', cmap='jet', plane_color=(0.5, 0.5, 0.5, 1)):
    '''
    Visualize flagella and the plane.
    - Color flagella in accordance with their phase
    - Assume first N objects - cilia/flagella, and N+1th object - plane
    '''
    source = FBEM.Source(path, group)

    colors_list = get_colors(num_phases, cmap=cmap)

    flagella_colors = []
    for phase in phases:
        color = colors_list[phase]
        flagella_colors.append(color)

    flagella_names = [f'flagellum_{i + 1}' for i in range(len(phases))]
    flagella_mesh = MeshViewer(path, group=group, colors=flagella_colors, names=flagella_names)

    plane_mesh = MeshViewer(path, group=group, names=['plane'], colors=[plane_color])

    m_combined = flagella_mesh + plane_mesh
    return m_combined
