import os, shutil
import unittest
import numpy as np
import numpy.testing as nptest
import FBEM
import mesh
import mesh.shapes as shapes
from angle_area import is_angle_satisfied, is_area_satisfied

basic_test_folder = 'data/triangulation/test/'
basic_expected_folder = 'data/triangulation/expected/'

rtol = 10 ** - 8
atol = 10 ** - 8


def load_data(folder):
    pos, tri = FBEM.read_all_triangulation_input(os.path.join(folder, 'input.dat'))
    return pos, tri


class TestShapes(unittest.TestCase):
    '''
    Test if I didn't accidently break mesh creation, compared to Gary's code.
    '''

    def test_flagellum(self):
        test_name = 'flagellum'
        folder_test = basic_test_folder + test_name
        shutil.rmtree(folder_test)
        os.makedirs(folder_test, exist_ok=False)

        s = np.linspace(0, 2, 10)

        radius = 0.1
        azimuth_grid = 5
        dt = 0.3
        xs, ys, zs = (np.sin(s / 3), np.cos(s / 3), s)
        positions = zip(xs, ys, zs)
        future_positions = zip(xs + 0.1, ys, zs + 1)

        flagellum_dict = {'type': 'flagellum',
                          'positions': positions,
                          'future positions': future_positions,
                          'radius': radius,
                          'azimuth grid': azimuth_grid,
                          'dt': dt}
        wrapped = {'flag': mesh.transform(flagellum_dict)}

        FBEM.write_input_and_ranges(folder_test, wrapped)

        coords_test, trias_test = load_data(folder_test)

        folder_expected = basic_expected_folder + test_name
        coords_expected, trias_expected = load_data(folder_expected)
        nptest.assert_allclose(coords_test, coords_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(trias_test, trias_expected, rtol=rtol, atol=atol)

    def test_cylinder(self):
        test_name = 'cylinder'
        folder_test = basic_test_folder + test_name

        shutil.rmtree(folder_test)
        os.makedirs(folder_test, exist_ok=False)

        s = np.linspace(0, 2, 10)

        radius = 0.1
        azimuth_grid = 5
        dt = 0.3
        xs, ys, zs = (np.zeros_like(s), np.zeros_like(s), s)
        positions = zip(xs, ys, zs)
        future_positions = zip(xs + 0.1, ys, zs + 1)

        flagellum_dict = {'type': 'flagellum',
                          'positions': positions,
                          'future positions': future_positions,
                          'radius': radius,
                          'azimuth grid': azimuth_grid,
                          'dt': dt}
        wrapped = {'flag': mesh.transform(flagellum_dict)}

        FBEM.write_input_and_ranges(folder_test, wrapped)

        coords_test, trias_test = load_data(folder_test)

        folder_expected = basic_expected_folder + test_name
        coords_expected, trias_expected = load_data(folder_expected)
        nptest.assert_allclose(coords_test, coords_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(trias_test, trias_expected, rtol=rtol, atol=atol)

    def test_ellipsoid(self):  # Test both sphere and ellipsoid
        test_name = 'ellipsoid'
        folder_test = basic_test_folder + test_name
        shutil.rmtree(folder_test)
        os.makedirs(folder_test, exist_ok=False)

        radius = 0.1
        position = (0, 0, 1)
        velocity = (0, 2, 0)

        sphere = mesh.sphere_create('sphere', position, radius, velocity, grid=6)
        ellipsoid = mesh.ellipsoid_create('ellipsoid',
                                          position=(-2, 0, 0),
                                          lengths=(3, 0.4, 0.3),
                                          axe1=(1, 0, 0),
                                          axe2=(0, 1, 0),
                                          velocity=(3, 0, 0),
                                          grid=4)

        system = mesh.join_systems(sphere, ellipsoid)
        FBEM.write_input_and_ranges(folder_test, system)

        coords_test, trias_test = load_data(folder_test)

        folder_expected = basic_expected_folder + test_name
        coords_expected, trias_expected = load_data(folder_expected)
        nptest.assert_allclose(coords_test, coords_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(trias_test, trias_expected, rtol=rtol, atol=atol)

    def test_plane(self):
        test_name = 'plane'
        folder_test = basic_test_folder + test_name

        shutil.rmtree(folder_test)
        os.makedirs(folder_test, exist_ok=False)

        sizeX, sizeY = 2, 6
        gridX, gridY = 3, 4
        width = 0.5
        plane = mesh.planeXY_create('plane', sizeX, sizeY, width, gridX, gridY, centers=None)

        radius = 0.1
        position = (0, 0, 1)
        velocity = (0, 0, -5)
        sphere = mesh.sphere_create('sphere', position, radius, velocity, grid=3)

        system = mesh.join_systems(sphere, plane)
        FBEM.write_input_and_ranges(folder_test, system)
        coords_test, trias_test = load_data(folder_test)

        folder_expected = basic_expected_folder + test_name
        coords_expected, trias_expected = load_data(folder_expected)
        nptest.assert_allclose(coords_test, coords_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(trias_test, trias_expected, rtol=rtol, atol=atol)

    def test_cuboid(self):
        test_name = 'cuboid'
        folder_test = basic_test_folder + test_name
        shutil.rmtree(folder_test)
        os.makedirs(folder_test, exist_ok=False)

        sizes = (2, 6, 0.5)
        grids = (3, 4, 3)
        velocityfield = lambda x, y, z: (2, 3, 4)
        cuboid = mesh.cuboidXY_create('cuboid', sizes, grids, velocityfield=velocityfield)

        FBEM.write_input_and_ranges(folder_test, cuboid)
        coords_test, trias_test = load_data(folder_test)

        folder_expected = basic_expected_folder + test_name
        coords_expected, trias_expected = load_data(folder_expected)
        nptest.assert_allclose(coords_test, coords_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(trias_test, trias_expected, rtol=rtol, atol=atol)


class TestFlatEllipse(unittest.TestCase):
    def test_areas(self):
        pass

    def test_triangulation(self):
        test_name = 'flat_ellipse'
        folder_test = basic_test_folder + test_name
        shutil.rmtree(folder_test)
        os.makedirs(folder_test, exist_ok=False)

        radiusX, radiusY, width = 4, 4, 10
        max_area, n_layers = 5.0265, 2
        position = (1, 23, 0)
        flat_ellipse = mesh.disk_create(name=test_name,
                                        radiusX=radiusX, width=width,
                                        max_area=max_area,
                                        extra_side_node_layers=n_layers,
                                        position=position)

        FBEM.write_input_and_ranges(folder_test, flat_ellipse)
        coords_test, trias_test = load_data(folder_test)

        folder_expected = basic_expected_folder + test_name
        coords_expected, trias_expected = load_data(folder_expected)
        nptest.assert_allclose(coords_test, coords_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(trias_test, trias_expected, rtol=rtol, atol=atol)

        self.assertTrue(is_angle_satisfied(coords_test, trias_test))


class TestFlagellum2(unittest.TestCase):
    def test_stationary(self):
        nTheta = 4
        xs = [0, 1, 3]
        r = 0.5
        points = [(x, 0, 0) for x in xs]
        tangents = [(1, 0, 0) for x in xs]
        normals = [(0, 1, 0) for x in xs]
        dt = 1

        c, v, t = shapes.prepareFlagella2(points, tangents, normals, r, nTheta,
                                          points, tangents, normals, dt)

        c_expected = [(0, 0, 0), (1, r, 0), (1, 0, r), (1, -r, 0), (1, 0, -r), (3, 0, 0)]
        v_expected = [(0, 0, 0) for _ in c_expected]
        t_expected = [[0, 1, 2],
                      [0, 2, 3],
                      [0, 3, 4],
                      [0, 4, 1],
                      [5, 2, 1],
                      [5, 3, 2],
                      [5, 4, 3],
                      [5, 1, 4]]
        nptest.assert_allclose(c, c_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(v, v_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(t, t_expected, rtol=rtol, atol=atol)

    def test_move_simple(self):
        nTheta = 4
        xs = [0, 1, 3]
        r = 0.5
        points = [(x, 0, 0) for x in xs]
        tangents = [(1, 0, 0) for x in xs]
        normals = [(0, 1, 0) for x in xs]

        dx = 15
        dz = 5
        dt = 0.1234
        points_next = [(x + dx, 0, dz) for x in xs]
        c, v, t = shapes.prepareFlagella2(points, tangents, normals, r, nTheta,
                                          points_next, tangents, normals, dt)

        c_expected = [(0, 0, 0), (1, r, 0), (1, 0, r), (1, -r, 0), (1, 0, -r), (3, 0, 0)]
        v_expected = [(dx / dt, 0, dz / dt) for _ in c_expected]
        t_expected = [[0, 1, 2],
                      [0, 2, 3],
                      [0, 3, 4],
                      [0, 4, 1],
                      [5, 2, 1],
                      [5, 3, 2],
                      [5, 4, 3],
                      [5, 1, 4]]
        nptest.assert_allclose(c, c_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(v, v_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(t, t_expected, rtol=rtol, atol=atol)

    def test_move_normal(self):
        nTheta = 4
        zs = [0, 1, 3]
        r = 0.614
        dt = 0.4
        points = [(0, 0, z) for z in zs]
        tangents = [(0, 0, 1) for z in zs]
        normals = [(1, 0, 0) for z in zs]

        alpha = 0.01  # rot angle; radian
        points_next = points
        tangents_next = tangents
        cos = np.cos(alpha)
        sin = np.sin(alpha)
        normals_next = [(cos, sin, 0) for n in normals]

        c, v, t = shapes.prepareFlagella2(points, tangents, normals, r, nTheta,
                                          points_next, tangents_next, normals_next, dt)

        c_expected = [(0, 0, 0),
                      (r, 0, 1), (0, r, 1),
                      (-r, 0, 1), (0, -r, 1), (0, 0, 3)]
        c_expected_next = [(0, 0, 0),
                           (r * cos, r * sin, 1), (- r * sin, r * cos, 1),
                           (-r * cos, - r * sin, 1), (r * sin, - r * cos, 1), (0, 0, 3)]

        v_expected = [(np.array(c1) - np.array(c0)) / dt for c0, c1 in zip(c_expected, c_expected_next)]
        t_expected = [[0, 1, 2],
                      [0, 2, 3],
                      [0, 3, 4],
                      [0, 4, 1],
                      [5, 2, 1],
                      [5, 3, 2],
                      [5, 4, 3],
                      [5, 1, 4]]
        nptest.assert_allclose(c, c_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(v, v_expected, rtol=rtol, atol=atol)
        nptest.assert_allclose(t, t_expected, rtol=rtol, atol=atol)
