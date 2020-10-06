"""
Visualzie using `vedo` (a.k.a. `vtkplotter`?) package

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
    colors = [c[:3] for c in colors] # only RGB, no alpha
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


#   m_combined = vedo.merge(*meshes) # loses individual colors
    m_combined = meshes[0]
    for m in meshes[1:]:
        m_combined += m
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
