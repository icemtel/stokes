'''
This file might work differently in the future! Don't reuse it
'''

import scipy as sp

import mesh
import myOS
import FMM.inputDat as inputDat


base_folder = 'expected_new'

# Flagellum
def write_flag():
    folder_expected = base_folder + '/flagellum'

    s = sp.linspace(0, 2, 10)

    radius = 0.1
    azimuth_grid = 5
    dt = 0.3
    xs, ys, zs = (sp.sin(s / 3), sp.cos(s / 3), s)
    positions = zip(xs, ys, zs)
    future_positions = zip(xs + 0.1, ys, zs + 1)

    flagellum_dict = {'type': 'flagellum',
                      'positions': positions,
                      'future positions': future_positions,
                      'radius': radius,
                      'azimuth grid': azimuth_grid,
                      'dt': dt}
    system = {'flag': mesh.transform(flagellum_dict)}

    with myOS.working_directory(folder_expected):
        with open('remembery.py', 'w') as remembery:
            if 'system' in system.keys():
                inputDat.writeInputAndRemembery_NEW(system, remembery=remembery)
            else:  # 'Transform the system, so the Gary's code runs OK.
                wrapped_system = mesh.transform(system)
                inputDat.writeInputAndRemembery_NEW(wrapped_system, remembery=remembery)


# Cylinder

def write_cylinder():
    folder_expected = base_folder + '/cylinder'

    s = sp.linspace(0, 2, 10)

    radius = 0.1
    azimuth_grid = 5
    dt = 0.3
    xs, ys, zs = (sp.zeros_like(s), sp.zeros_like(s), s)
    positions = zip(xs, ys, zs)
    future_positions = zip(xs + 0.1, ys, zs + 1)

    flagellum_dict = {'type': 'flagellum',
                      'positions': positions,
                      'future positions': future_positions,
                      'radius': radius,
                      'azimuth grid': azimuth_grid,
                      'dt': dt}
    system = {'flag': mesh.transform(flagellum_dict)}

    with myOS.working_directory(folder_expected):
        with open('remembery.py', 'w') as remembery:
            if 'system' in system.keys():
                inputDat.writeInputAndRemembery_NEW(system, remembery=remembery)
            else:  # 'Transform the system, so the Gary's code runs OK.
                wrapped_system = mesh.transform(system)
                inputDat.writeInputAndRemembery_NEW(wrapped_system, remembery=remembery)



def write_ellipsoid():
    folder_expected = base_folder + '/ellipsoid'
    radius = 0.1
    position = (0, 0, 1)
    velocity = (0, 2, 0)

    sphere_dict = {'type': 'ellipsoid',
                   'position': position,  # - in Gary's code ellipse is always created in (0,0,0) -> add translation
                   'lengths': (radius, radius, radius), 'axe1': (1, 0, 0), 'axe2': (0, 1, 0), 'grid': 6}

    '''
    {'type': 'ellipsoid',
                'position': (0, 0, 0),
                'lengths': lengths, 'axe1': axe1, 'axe2': axe2, 'grid': grid}
    '''

    position2 = (-2, 0, 0)
    lengths = (3, 0.4, 0.3)
    axe1 = (1, 0, 0)
    axe2 = (0, 1, 0)
    velocity2 = (3, 0, 0)
    grid2 = 4
    ellipsoid_dict = {'type': 'ellipsoid',
                      'position': (0, 0, 0),  # - in Gary's code ellipse is always created in (0,0,0) -> add translation
                      'lengths': lengths, 'axe1': axe1, 'axe2': axe2, 'grid': grid2}

    system = {'sphere': mesh.transform(sphere_dict, velocity=velocity, translation=position),
              'ellipsoid': mesh.transform(ellipsoid_dict, velocity=velocity2, translation=position2)}

    with myOS.working_directory(folder_expected):
        with open('remembery.py', 'w') as remembery:
            if 'system' in system.keys():
                inputDat.writeInputAndRemembery_NEW(system, remembery=remembery)
            else:  # 'Transform the system, so the Gary's code runs OK.
                wrapped_system = mesh.transform(system)
                inputDat.writeInputAndRemembery_NEW(wrapped_system, remembery=remembery)



def write_plane():
    folder_expected = base_folder + '/plane'

    sizeX, sizeY = 2, 6
    gridX, gridY = 3, 4
    width = 0.5
    plane = plane_dict = {'type': 'plane',
                          'p0': (-sizeX / 2, -sizeY / 2, - width),
                          'p1': (sizeX / 2, -sizeY / 2, -width),
                          'p2': (-sizeX / 2, sizeY / 2, -width),
                          'width': width, 'grid1': gridX, 'grid2': gridY, 'centers': []}

    radius = 0.1
    position = (0, 0, 1)
    velocity = (0, 0, -5)
    sphere_dict = {'type': 'ellipsoid',
                   'position': position,  # - in Gary's code ellipse is always created in (0,0,0) -> add translation
                   'lengths': (radius, radius, radius), 'axe1': (1, 0, 0), 'axe2': (0, 1, 0), 'grid': 3}

    system = {'sphere': mesh.transform(sphere_dict, velocity=velocity, translation=position),
              'plane': mesh.transform(plane_dict)}

    with myOS.working_directory(folder_expected):
        with open('remembery.py', 'w') as remembery:
            if 'system' in system.keys():
                inputDat.writeInputAndRemembery_NEW(system, remembery=remembery)
            else:  # 'Transform the system, so the Gary's code runs OK.
                wrapped_system = mesh.transform(system)
                inputDat.writeInputAndRemembery_NEW(wrapped_system, remembery=remembery)



def write_cuboid():
    '''
    In GK's code rectangle=cuboid
    '''
    folder_expected = base_folder + '/cuboid'
    sizes = (2, 6, 0.5)
    grids = (3, 4, 3)
    velocityfield = lambda x, y, z: (2, 3, 4)

    sizeX, sizeY, sizeZ = sizes
    gridX, gridY, gridZ = grids
    rectangle_dict = {'type': 'rectangle',
                      'p0': (-sizeX / 2, -sizeY / 2, - sizeZ),
                      'p1': (sizeX / 2, -sizeY / 2, -sizeZ),
                      'p2': (-sizeX / 2, sizeY / 2, -sizeZ),
                      'p3': (-sizeX / 2, -sizeY / 2, 0),
                      'grid1': gridX, 'grid2': gridY, 'grid3': gridZ,
                      'velocityfield': velocityfield}

    system = {'cuboid': mesh.transform(rectangle_dict)}

    with myOS.working_directory(folder_expected):
        with open('remembery.py', 'w') as remembery:
            if 'system' in system.keys():
                inputDat.writeInputAndRemembery_NEW(system, remembery=remembery)
            else:  # 'Transform the system, so the Gary's code runs OK.
                wrapped_system = mesh.transform(system)
                inputDat.writeInputAndRemembery_NEW(wrapped_system, remembery=remembery)



def write_flat_ellipse():
    '''
    My new mesh object
    '''
    folder_expected = base_folder + '/flat_ellipse'
    radiusX, radiusY, width = 4, 4, 10
    n_elems, n_layers = 10, 2
    position = (1, 23, 0)
    flat_ellipse = mesh.flat_ellipse_create(name='flat_ellipse',
                                            radiusX=radiusX, radiusY=radiusY, width=width,
                                            n_elems=n_elems,
                                            extra_side_node_layers=n_layers,
                                            position=position)
    import FBEM
    FBEM.write_input_and_remembery(folder_expected, flat_ellipse)


write_flag()
write_cylinder()
write_ellipsoid()
write_plane()
write_cuboid()

#write_flat_ellipse()
