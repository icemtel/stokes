'''
Setup for cilia geometry
'''
import os
import numpy as np
import mesh

shapes_data_path = os.path.dirname(__file__) + '/shapes_data'
data_key = 'machemer'
num_phases = 20
dphi = 2 * np.pi / num_phases

# Phyiscal values
beat_period = 31.25  # ms; 32 Hz
beat_freq = 2 * np.pi / beat_period
beat_time_step = beat_period / num_phases  # ms
flag_length = 10  # um; from the data


def data_loader(*filenames):
    '''
    Load cilia shapes;
    - skip every n-th data point in the middle of the cilium:
    - keep refined spacing near the tips
    :param filenames: Names of files to contain x,y,z data
    :return: A function which returns np.array: rs = [[x1,y1,z1],[x2,y2,z2],..]

    TODO: maybe needs better testing
    now know that it works well with near_tip_skip=0, and longtitude_grid = n * (len(data) - 1)
    '''

    def load_data(phase, longitude_grid, near_tip_skip=0):
        '''
        :param phase:
        :param longitude_grid: approximately number of points along the cilium
        :param near_tip_skip: =0 means the end of cilium will be flat
        :return:
        '''
        xs = []
        for filename in filenames:
            x = np.loadtxt(os.path.join(shapes_data_path, filename))[phase]
            xs.append(x)
        vals = np.array(xs).transpose()  # e.g. xs = [xx,yy,zz] => vals = [[x1,y1,z1],[x2,y2,z2],..]
        num_points = len(vals)

        # Explicitly define indices to keep, other data points will not be used
        spacing = (num_points - 2 * near_tip_skip) // longitude_grid
        indices = [0] +  list(np.arange(near_tip_skip, num_points - near_tip_skip, spacing)) + [num_points - 1]
        vals = vals[indices]
        return vals

    return load_data


# Define commands to load coordinates, tangent vectors, normal vectors, and phase-derivative of coordinates dr/dphi
load_rr = data_loader('x-data', 'y-data', 'z-data')
load_tangents = data_loader('tx-data', 'ty-data', 'tz-data')
load_normals = data_loader('nx-data', 'ny-data', 'nz-data')
load_drrdphi = data_loader('dxdphi-data', 'dydphi-data', 'dzdphi-data')


def create_flagellum(idx, phase, phase_speed, translation, rotation,
                     flag_radius, longitude_grid, azimuth_grid):
    """
    :param phase_speed: integer; will be multiplied by default frequency
    :param longitude_grid: how man
    :param azimuth_grid: number of grid points (integer)
    :return:
    """
    points = load_rr(phase, longitude_grid=longitude_grid)
    tangents = load_tangents(phase, longitude_grid=longitude_grid)
    normals = load_normals(phase, longitude_grid=longitude_grid)
    drrdphi = load_drrdphi(phase, longitude_grid=longitude_grid)
    velocities = phase_speed * drrdphi * beat_freq
    name = 'flagellum_' + str(idx + 1)
    flagellum = mesh.flagellum_vel_create(name=name,
                                          points=points,
                                          velocities=velocities,
                                          tangents=tangents,
                                          normals=normals,
                                          radius=flag_radius,
                                          azimuth_grid=azimuth_grid,
                                          translation=translation,
                                          rotation=rotation)
    return flagellum


def create_plane(plane_radius, plane_width, max_plane_elem_area, refinement):
    plane = mesh.disk_create('plane', plane_radius, plane_width, max_area=max_plane_elem_area,
                             extra_side_node_layers='auto',
                             refinement=refinement, refine_bot=False)
    return plane


def create_cilia(translations, rotations,
                 phase_vector, phase_speed,
                 flag_radius, azimuth_grid,
                 longitude_grid):
    # Check that only one cilium is moving
    assert np.sum(phase_speed) == 1

    flagella = {}
    for (i, phase) in enumerate(phase_vector):
        flagellum = create_flagellum(i, phase, phase_speed[i], translations[i], rotations[i], flag_radius,
                                     longitude_grid, azimuth_grid)
        flagella.update(flagellum)

    return flagella

def create_cilia_and_plane(translations, rotations,
                           phase_vector, phase_speed,
                           flag_radius, azimuth_grid,
                           longitude_grid,
                           plane_radius, plane_width, max_plane_elem_area, refinement):
    '''
    Define Geometry with cilia and a plane. General 3D case
    :param phase_speeds: tuple/array/list of integers; the same dimensions as phase_vector
    :param translations: positions of cilia in 3D
    '''
    flagella = create_cilia(translations, rotations, phase_vector, phase_speed,
                            flag_radius, azimuth_grid, longitude_grid)
    plane = create_plane(plane_radius, plane_width, max_plane_elem_area, refinement)
    system = mesh.join_systems(flagella, plane)

    return system

if __name__ == '__main__':
    phase = 0

    # Count lenght of the cilium
    rr = load_rr(phase, longitude_grid=30)
    print(rr[:2], rr[-2:])

    length = 0
    for r0, r1 in zip(rr, rr[1:]):
        ds = np.linalg.norm(r0 - r1)
        length += ds

    print(length)

    flagellum = create_flagellum(1, phase, 0, [0,0,0], np.eye(3), 0.1, 60, 5)
    plane = create_plane(plane_radius=20, plane_width=1, max_plane_elem_area=10, refinement=None)

    system = mesh.join_systems(flagellum, plane)
    system = mesh.prepare_system(system)

    triangulation = mesh.triangulate_system(system)

    import mesh.plot.trimesh_viewer as mplot

    m = mplot.triangulation_to_trimesh(triangulation)
    m.show()