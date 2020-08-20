"""
This file is called by routine which creates mesh from nested dictionaries (convert.py).
"""
import numpy as np
import mesh.orient as orient
import mesh.triangulate2D as tri
from mesh.shapes.Regions2D import RefinementCircle, RefinementMany


def triangulate_sides(width,
                      coords_upper, coords_lower, boundary_points,
                      trias,
                      extra_side_layers=0):
    '''
    Connect initial (boundary) nodes of upper and lower planes by triangular elements.
    Returns the array with triangle indices.
    The orientation is correct - tested
    '''
    if extra_side_layers == 'auto':
        boundary_points_distance = np.linalg.norm(boundary_points[1] - boundary_points[0])
        extra_side_layers = get_layers_number_auto(width, boundary_points_distance)
    # Define boundary layers points
    boundary_points_top = np.array([(x, y, 0) for (x, y) in boundary_points])
    layers = [boundary_points_top - (0, 0, width * k / (extra_side_layers + 1))  # TODO: also rotate intermediate layers
              for k in range(extra_side_layers + 2)]
    # Now go through each pair of consequent layers and connect them with triangles.
    idx_first = 0
    idx_second = len(coords_upper) + len(coords_lower)
    num = len(boundary_points)
    trias_to_concatenate = [trias]
    for id, (layer, next_layer) in enumerate(zip(layers, layers[1:])):
        if id < extra_side_layers:
            trias_to_add = connect_layers(idx_first, idx_second, num)
            trias_to_concatenate.append(trias_to_add)
            idx_first = idx_second
            idx_second += num
        # Connect the last layer
        if id == extra_side_layers:
            idx_second = len(coords_upper)  # coords_lower start right after coords_upper
            trias_to_add = connect_layers(idx_first, idx_second, num)
            trias_to_concatenate.append(trias_to_add)

    trias = np.concatenate(trias_to_concatenate)
    coords_to_concatenate = [coords_upper, coords_lower] + layers[1:-1]
    coords = np.concatenate(coords_to_concatenate)
    return coords, trias


def get_layers_number_auto(width, boundary_points_distance):
    '''
    Normally mesh is created with restriction of minimal angle to 20 degrees.
    Use the same restriction to set distance between boundary layers.
    If we use a triangle with right angle ->
     distance between layers should be equal or less than 2.74748 of boundary points distance.
    If triangle is symetrical and has angles of 20,80,80 degrees ->
    then coefficient is a bit bigger - 2.836 (double-check)
    Numbers are obtained just by finding sides of triangle with given angles.
    UPD: Better triangle quality - change k to = 2
    '''
    k = 2 # 2.747
    spacing = boundary_points_distance * k
    num_extra_layers = max(0, int(width / spacing - 1))  # -1 because we already have 1 connection between bot and top sides
    return num_extra_layers


def connect_layers(idx_first, idx_second, num):
    '''
    Connects nodes, which numbers are [idx_first, idx_first + num].
    Numbers of nodes to connect are [idx_second, idx_second + num].
    Connection in triangles.
    :return: triangulation list
    '''

    trias = []
    for n in range(0, num - 1):
        trias.append([idx_first + n, idx_first + n + 1, n + idx_second])
        trias.append([n + idx_second + 1, n + idx_second, idx_first + n + 1])
    trias.append([idx_first + num - 1, idx_first, idx_second + num - 1])
    trias.append([idx_second, idx_second + num - 1, idx_first])
    return trias


def prepareFlatEllipse(max_area,
                       radiusX, radiusY, width,
                       extra_side_layers=0,
                       refinement=None, type=None, refine_bot=True):
    '''
    refinement - Refinement class from Refinement2D
    :param refine_bot: Whether to refine both top and bot planes, or only top.
    '''
    # Check for errors
    if type != 'flat_ellipse':
        raise TypeError
    if radiusY is None or radiusX == radiusY:
        radiusY = radiusX
    else:
        raise NotImplementedError  # TODO: define the number of boundary points, and spacing
    if width is None:
        raise NotImplementedError  # TODO: Set width depening on element size

    #  Get initial points on outer boundary
    n_circle = tri.get_number_of_circle_points2(radiusX, max_area)
    boundary_points = tri.points_on_ellipse(n_circle, radiusX, radiusY)
    # Get triangulation in refined areas
    if refinement is not None:
        points_refined_region, _ = refinement.produce_mesh()
        points_list = [boundary_points, points_refined_region]
        points = np.concatenate(points_list)
    else:
        points = boundary_points
    # Get 2D triangulation of the top face of the plane
    coords_top, trias_top= tri.triangulate_with_triangle(points, max_area, add_code='')
    # Transform to 3D
    num_nodes = len(coords_top)
    coords_top = np.array([[coord[0], coord[1], 0] for coord in coords_top])

    if refine_bot or refinement is None:
        coords_bot = coords_top - (0, 0, width)
        trias_bot = trias_top # set the same triangulation on the lower plane. Only numeration is shifted
    else:
        coords2D_bot, trias_bot = tri.triangulate_with_triangle(boundary_points, max_area, add_code='')
        coords_bot = np.array([[coord[0], coord[1], - width] for coord in coords2D_bot])
    trias_bot = trias_bot + num_nodes  # set the same triangulation on the lower plane. Only numeration is shifted

    trias = np.concatenate((trias_top, trias_bot))
    # And triangulate side boundaries
    coords, trias = triangulate_sides(width, coords_top, coords_bot,
                                      boundary_points, trias, extra_side_layers)
    # Check and fix orientation
    origin = (0, 0, - width / 2)
    trias = orient.orientateTriangulation(origin, coords, trias)


    c = np.array(coords)
    v = np.zeros_like(coords)
    t = np.array(trias)
    return (c, v, t)



def prepare_flat_ellipse_old_style(n_elems,
                                   radiusX, radiusY, width,
                                   extra_side_layers=0,
                                   centers=None, type=None):
    '''
    Centers of the form (xy, r_zone, num_elems)
    '''
    # Check for errors
    if type != 'flat_ellipse':
        raise TypeError
    if radiusY is None or radiusX == radiusY:
        radiusY = radiusX
    else:
        raise NotImplementedError  # TODO: define the number of boundary points, and spacing
    if width is None:
        raise NotImplementedError  # TODO: Set width depening on element size

    max_area = np.pi * radiusX * radiusY / n_elems
    print(max_area)
    refinement = None
    if centers is not None:
        center_regions_list = []
        for center in centers:
            xy, r_center, num_elems_center = center
            max_area_center = np.pi * r_center ** 2 / num_elems_center
            center_region = RefinementCircle(xy, r_center, max_area_center)
            center_regions_list.append(center_region)
        refinement = RefinementMany(center_regions_list)

    return prepareFlatEllipse(max_area,
                              radiusX, radiusY, width,
                              extra_side_layers,
                              refinement, type)


if __name__ == "__main__":
    '''
    Run some testing
    '''
    import matplotlib.pyplot as plt


    n_elems = 30
    radiusX = 10
    radiusY = None
    extra_layers = 'auto'  # 2
    width = 3 * radiusX
    centers = [((0, 0), 3, 10)] #, ((50.5, 0), 2, 10)]
    type = 'flat_ellipse'
    c, v, t = prepare_flat_ellipse_old_style(n_elems, radiusX=radiusX, radiusY=radiusY, width=width,
                                             extra_side_layers=extra_layers,
                                             centers=centers, type=type)

    # Print some stuff
    n_boundary_nodes = tri.n_circle_from_n_elems(n_elems)
    boundary_node_distance = 2 * radiusX * np.sin(np.pi / n_boundary_nodes)
    print(boundary_node_distance)

    # Plot
    from mpl_toolkits.mplot3d import Axes3D # for 3d plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x, y, z = c.transpose()
    ax.plot(x, y, z, 'o')
    for tria in t:
        for id1, id2 in zip(tria, tria[1:]):
            x, y, z = np.array([c[id1], c[id2]]).transpose()
            plt.plot(x, y, z, color='blue')
        x, y, z = np.array([c[tria[0]], c[tria[-1]]]).transpose()
        ax.plot(x, y, z, color='blue')

    plt.show()