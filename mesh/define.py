'''
Definitions of geometrical objects.
'''

import numpy as np
from mesh.operate import transform


def ellipsoid_create(name, position=(0, 0, 0),
                     lengths=(1, 1, 1),
                     axe1=(1, 0, 0),
                     axe2=(0, 1, 0),
                     velocity=(0, 0, 0),
                     angular=(0, 0, 0),
                     grid=30):
    ellipsoid_dict = {'type': 'ellipsoid',
                      'position': (0, 0, 0),  # - in Gary's code ellipse is always created in (0,0,0) -> add translation
                      'lengths': lengths, 'axe1': axe1, 'axe2': axe2, 'grid': grid}

    wrapped = {name: transform(ellipsoid_dict,
                               velocity=velocity, angular=angular,
                               translation=position)}  # Add translation, because setting a position is bugged
    return wrapped


def sphere_create(name, position=(0, 0, 0), radius=1, velocity=(0, 0, 0), angular=(0, 0, 0), grid=30):
    lengths = (radius, radius, radius)
    return ellipsoid_create(name, position, lengths, velocity=velocity, angular=angular, grid=grid)


def plane_create(name,
                 p0=(-1, -1, -1),
                 p1=(1, -1, -1),
                 p2=(-1, 1, -1),
                 width=1,
                 grid1=3,
                 grid2=3,
                 centers=None):
    '''
    Plane starting at p0, to p1 and p2, with given width (in direction (p1-p0)x(p2-p0))
    Mesh will have increased density in centers (not tested)
    Number of elements equals
    """'''
    if centers == None:  # Using None as a default value, because [] is mutable
        centers_GK = []  # Now change it to [], because that's what is used in Gary's code
    else:
        centers_GK = centers
    plane_dict = {'type': 'plane',
                  'p0': p0, 'p1': p1, 'p2': p2,
                  'width': width, 'grid1': grid1, 'grid2': grid2, 'centers': centers_GK}

    wrapped = {name: transform(plane_dict)}
    return wrapped


def planeXY_create(name, sizeX, sizeY, width, gridX, gridY, centers=None):
    '''
    Simplified plane creation
    '''
    if centers == None:  # Using None as a default value, because [] is mutable
        centers_GK = []  # Now change it to [], because that's what is used in Gary's code
    else:
        centers_GK = centers
    plane_dict = {'type': 'plane',
                  'p0': (-sizeX / 2, -sizeY / 2, - width),
                  'p1': (sizeX / 2, -sizeY / 2, -width),
                  'p2': (-sizeX / 2, sizeY / 2, -width),
                  'width': width, 'grid1': gridX, 'grid2': gridY, 'centers': centers_GK}

    wrapped = {name: transform(plane_dict)}
    return wrapped


def cuboid_create(name,
                  p0=(0, 0, 0), p1=(0, 1, 0), p2=(0, 0, 1), p3=(1, 0, 0),
                  grid1=3, grid2=3, grid3=3,
                  velocityfield=lambda x, y, z: (0, 0, 0)):
    '''
    Meshed by GK.
    Create a cuboid (rectangular or not), similar to plane, p0,p1,p2,p3  - defining vertices of the cuboid.
    In each direction will be grid1+1, grid2+1, grid3+1 points - directions correspond to p1-p0,p2-p0, p3-p0.
    No 'centers' parameter. Velocity field can be used to prescribe velocities.
    '''
    rectangle_dict = {'type': 'cuboid',
                      'p0': p0, 'p1': p1, 'p2': p2, 'p3': p3,
                      'grid1': grid1, 'grid2': grid2, 'grid3': grid3,
                      'velocityfield': velocityfield}
    wrapped = {name: transform(rectangle_dict)}
    return wrapped


def cuboidXY_create(name, sizes, grids, velocityfield=lambda x, y, z: (0, 0, 0)):
    '''
    Create a cuboid, s.t. the top surface lies in XY plane,
    (0,0,0) is the center of this surface and edges a parallel to x- and y- axes.
    sizes - tuple of sizeX,sizeY,sizeZ
    grids - tuple of gridX, gridY,gridZ
    '''
    sizeX, sizeY, sizeZ = sizes
    gridX, gridY, gridZ = grids
    rectangle_dict = {'type': 'cuboid',
                      'p0': (-sizeX / 2, -sizeY / 2, - sizeZ),
                      'p1': (sizeX / 2, -sizeY / 2, -sizeZ),
                      'p2': (-sizeX / 2, sizeY / 2, -sizeZ),
                      'p3': (-sizeX / 2, -sizeY / 2, 0),
                      'grid1': gridX, 'grid2': gridY, 'grid3': gridZ,
                      'velocityfield': velocityfield}
    wrapped = {name: transform(rectangle_dict)}
    return wrapped


def flat_ellipse_create(name, n_elems,
                        radiusX, radiusY=None, width=None,
                        position=(0, 0, 0), rotation=np.diag([1, 1, 1]),
                        extra_side_node_layers=0,
                        centers=None):
    raise NotImplementedError('Roll back to June 2018 version')


def disk_create(name, radiusX, width, max_area,
                position=(0, 0, 0), rotation=np.diag([1, 1, 1]),
                extra_side_node_layers=0,
                refinement=None, refine_bot=True):
    '''
    Create flat (sandwich-like) circle using triangle library.
    By default the object is created in the center of xy-plane, but can be moved or rotated by setting 'position' & 'normal'
    :param max_area: Set max element area in Triangle input
    :param refinement: One of the classes defining the refinement.
            refinement.produce_mesh() will be called, and the output points will be added to the mesh
    :param extra_side_node_layers - add additional node layers in the surface,
            connecitng upper and lower part of the ellipse
            'auto' - choose number of layers automatically, s.t. min angle constraint is satisfied.
    :return: dict with the circle data
    '''
    radiusY = radiusX
    disk = dict(type='flat_ellipse',
                radiusX=radiusX, radiusY=radiusY, width=width,
                max_area=max_area, extra_side_layers=extra_side_node_layers,
                refinement=refinement, refine_bot=refine_bot)

    wrapped = {name: transform(disk, translation=position, rotation=rotation)}
    return wrapped


def flagellum2_create(name,
                      points, tangents, normals, radius, azimuth_grid,
                      points_next=None, tangents_next=None, normals_next=None, dt=None,
                      translation=(0, 0, 0), rotation=np.diag([1, 1, 1])):
    '''
    - If no "next" params are given, assume that flagellum is not moving.
      Otherwise, calculate velocities using finite difference.
    - v1: did not include tangents, normals;
        removed on 2021-06-07 [kept in legacy branch]

    :param normals: a list of normals (one for each point) ->
                   mesh on a circular crossection is generated starting from the direction of that normal.
                   (makes it easier to compare different shapes)
    '''
    if points_next is None and tangents_next is None and normals_next is None and dt is None:
        points_next = points
        tangents_next = tangents
        normals_next = normals
        dt = 1
    flagellum_dict = {'type': 'flagellum2',
                      'points': points,
                      'tangents': tangents,
                      'normals': normals,
                      'points_next': points_next,
                      'tangents_next': tangents_next,
                      'normals_next': normals_next,
                      'dt': dt,
                      'radius': radius,
                      'nTheta': azimuth_grid}
    wrapped = {name: transform(flagellum_dict, translation=translation, rotation=rotation)}
    return wrapped


def flagellum_vel_create(name, points, velocities, tangents, normals, radius, azimuth_grid,
                         translation=(0, 0, 0), rotation=np.diag([1, 1, 1])):
    '''
    Flagellum "ver 1.5" - specify velocities of centerline points; and also tangents and normals in each of these points.
    '''
    flagellum_dict = {'type': 'flagellumVel',
                      'points': points,
                      'vels': velocities,
                      'tangents': tangents,
                      'normals': normals,
                      'radius': radius,
                      'nTheta': azimuth_grid}
    wrapped = {name: transform(flagellum_dict, translation=translation, rotation=rotation)}
    return wrapped


def flagellum_vel_norm_create(name, points, velocities, tangents, normals, normal_velocities, radius, azimuth_grid,
                              translation=(0, 0, 0), rotation=np.diag([1, 1, 1])):
    '''
    :param normal_velocities: dndt - rate of change of normals; used to calculate velocites.
    CAUTION: Works only for 2D beat pattern
    '''
    flagellum_dict = {'type': 'flagellumVelNorm',
                      'points': points,
                      'vels': velocities,
                      'tangents': tangents,
                      'normals': normals,
                      'normal_vels': normal_velocities,
                      'radius': radius,
                      'nTheta': azimuth_grid}
    wrapped = {name: transform(flagellum_dict, translation=translation, rotation=rotation)}
    return wrapped


