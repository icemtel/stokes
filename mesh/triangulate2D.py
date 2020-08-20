'''
Use `trianle library` to create mesh.
'''
import numpy as np


def triangulate_with_triangle(points, max_area, add_code=''):
    '''
    Create triangulation using *triangle* library (don't forget to cite it)
    Parameters: q - quality meshing (restrict triangles angles to be >20 degrees),
                a - restriction on maximum triangle area,
                Y - forbid to put new points on the boundary -
                 to make sure we connect top and bottom sides of ellipse correctly
                 NB: make sure there are enough points on outer boundary to generate a good mesh
    https://www.cs.cmu.edu/~quake/triangle.switch.html
    '''
    import triangle

    tri_data = {'vertices': points}
    code = 'qa{0:.31f}'.format(max_area) + add_code
    tri = triangle.triangulate(tri_data, code)

    coords = tri['vertices']
    trias = tri['triangles']
    return coords, trias


# Triangulate circle

def n_circle_from_n_elems(n_elems):
    '''
    max_area = sp.pi * total_radius **2 / n_elems
    node_distance = 2 * 3 ** (-1/4)* max_area ** (1/2)
    num_nodes_on_boundary =~ (2 *sp.pi * total_radius) / node_distance
    => num_nodes_on_boundary = int(3 ** (1/4) * (sp.pi * n_elems) ** (1/2)
    '''
    return int((np.pi * n_elems) ** (1 / 2) * 3 ** (1 / 4))


def get_number_of_circle_points2(radius, max_area):
    k = 2 * 3 ** (-1 / 4)  # Coeff to connect linear and area-sizes of triangle.
    node_distance = k * np.sqrt(max_area)
    num_nodes_on_boundary = int(2 * np.pi * radius / node_distance)
    return num_nodes_on_boundary


def get_number_of_boundary_points_ellipse(lengths, max_area):
    k = 2 * 3 ** (-1 / 4)  # Coeff to connect linear and area-sizes of triangle.
    node_distance = k * np.sqrt(max_area)
    a, b = lengths
    ellipse_perimeter = np.pi * (3 * (a + b) - np.sqrt((3 * a + b) * (a + 3 * b))) # Ramanujan's approximation
    num_nodes_on_boundary = int(ellipse_perimeter / node_distance)
    return num_nodes_on_boundary


def points_on_ellipse(n, length1, length2=None, rotation_angle=0, center=(0, 0), starting_angle=0):
    '''
    lx, ly - lengths of semi-axes of ellipse
    starting at `starting_angle` (radians)
    :param rotation_angle: angle between x-axis and ellipse first axis (radians) angle > 0
    => rotate ellipse counter-clockwise
    TODO: more safisticated spacing for lx != ly - but it's much more complicated!
    '''
    if length2 is None:
        length2 = length1
    dphi = 2 * np.pi / n
    angle = starting_angle
    points = []
    for i in range(n):
        x = length1 * np.cos(angle)
        y = length2 * np.sin(angle)
        angle += dphi
        points.append((x, y))
    # Apply rotation and translation transformations
    c, s = np.cos(rotation_angle), np.sin(rotation_angle)
    rotation = np.array([[c, -s], [s, c]])
    points = [np.dot(rotation, point) + center for point in points]
    return np.array(points)


def triangulate_circle(center, radius, max_area, add_code='', add_points=None):
    '''
    :param center:
    :param radius:
    :param max_area:
    :param add_code:
    :param add_points: points to include in the mesh
    :return:
    '''
    n_circle = get_number_of_circle_points2(radius, max_area)
    assert n_circle > 4  # If there's less than 5 boundary points - that's probably not what I want - stop the program
    boundary_points = points_on_ellipse(n_circle, radius, radius, center=center)
    if add_points is not None:
        initial_points = np.concatenate((boundary_points, add_points), axis=0)
    else:
        initial_points = boundary_points
    coords, trias = triangulate_with_triangle(initial_points, max_area, add_code)
    return coords, trias


def triangulate_ellipse(center, lengths, max_area, rotation_angle=0, add_code='',add_points=None):
    '''
    At length ratio = 3 (and maybe even lower) this function can only be used on inner regions;
    Some points will be added to boundary by Triangle.
    :param add_points: points to include in the mesh
    '''
    n_boundary = get_number_of_boundary_points_ellipse(lengths, max_area)
    assert n_boundary > 4  # If there's less than 5 boundary points - that's probably not what I want - stop the program
    boundary_points = points_on_ellipse(n_boundary, lengths[0], lengths[1], rotation_angle, center)
    if add_points is not None:
        initial_points = np.concatenate((boundary_points, add_points), axis=0)
    else:
        initial_points = boundary_points
    coords, trias = triangulate_with_triangle(initial_points, max_area, add_code)
    return coords, trias


if __name__ == '__main__':
    '''
    OK: add_points
    '''
    import matplotlib.pyplot as plt


    lengths = (10,5)
    max_area = 3

    n_boundary = get_number_of_boundary_points_ellipse(lengths, max_area)
    add_points = np.array([[1, 0], [-1, 0], [0, 0], [0, -1], [0, 1]])
    points = points_on_ellipse(n_boundary, lengths[0], lengths[1], rotation_angle=np.pi / 4, center= 5)
    c, t = triangulate_ellipse(5, lengths, max_area, rotation_angle=np.pi / 4, add_points=add_points)

    x0,y0 = points.transpose()
    x,y = c.transpose()

    plt.triplot(x,y,t)
    plt.scatter(x0,y0, c='red')
    plt.scatter(add_points[:,0], add_points[:,1],c='green')
    plt.show()