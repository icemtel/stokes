import os, shutil
import unittest
import numpy.testing as nptest

import mesh
import FBEM
import simulation.parallel_with_threads as pwt

rtol = 10 ** - 8
atol = 10 ** - 8


def run_simulation(folder, size):
    sphere = mesh.sphere_create('sphere', radius=size, velocity=(1, 0, 0), grid=3)
    FBEM.run(sphere, folder)


basic_folder = 'data/parallel/'


class test_spheres_parallel(unittest.TestCase):
    '''
    Compare results of mesh creation + FBEM obtained in parallel to results by sequential code (pre-computed).
    '''

    def test_spheres(self):
        testname = 'spheres'
        basic_test_folder = os.path.join(basic_folder, testname, 'test')
        shutil.rmtree(basic_test_folder)

        radii = [k for k in range(1, 5)]
        test_folders = [os.path.join(basic_test_folder, 'radius_{0}'.format(radius)) for radius in radii]
        args = list(zip(test_folders, radii))

        pwt.run_parallel(2, run_simulation, args)

        for i, radius in enumerate(radii):
            data_test = FBEM.extract_all_data(test_folders[i])

            folder_expected = os.path.join(basic_folder, testname, 'expected', 'radius_{0}'.format(radius))
            data_expected = FBEM.extract_all_data(folder_expected)
            coords_test, coords_expected = data_test.coordinates, data_expected.coordinates
            vels_test, vels_expected = data_test.velocities, data_expected.velocities
            forces_test, forces_expected = data_test.forces, data_expected.forces
            nptest.assert_allclose(coords_test, coords_expected, rtol=rtol, atol=atol)
            nptest.assert_allclose(vels_test, vels_expected, rtol=rtol, atol=atol)
            nptest.assert_allclose(forces_test, forces_expected, rtol=rtol, atol=atol)
