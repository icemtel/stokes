'''
Check mesh constraints
'''

import unittest
import numpy.testing as nptest

import numpy as np
import scipy.linalg as lin

import mesh
from angle_area import is_angle_satisfied, is_area_satisfied

rtol = 10 ** - 8
atol = 10 ** - 8


class TestCircleRefinement(unittest.TestCase):
    def test_mesh(self):
        center = 5, 4
        radius = 7
        max_area = 5
        region = mesh.RefinementCircle(center, radius, max_area)
        coords, trias = region.produce_mesh()

        x0, y0 = center
        for x, y in coords:
            assert ((x - x0) ** 2 + (y - y) ** 2) < radius ** 2 * (1 + rtol) ** 2

        self.assertTrue(is_area_satisfied(coords, trias, max_area))
        self.assertTrue(is_angle_satisfied(coords, trias))

    def test_distance_point(self):
        center = 100, -5.2
        radius = 3
        max_area = 1.3
        region = mesh.RefinementCircle(center, radius, max_area)

        point = 100, 0
        dist_actual = region.distance_to_point(point)
        dist_desired = 2.2
        nptest.assert_allclose(dist_actual, dist_desired, rtol=rtol, atol=atol)

    def test_distance_region(self):
        center = 0, -3.1
        radius = 3
        max_area = 1.3
        region1 = mesh.RefinementCircle(center, radius, max_area)
        # Test distance to a different region
        translation = 10, -10
        center2 = np.array(center) + translation
        radius2 = 5
        region2 = mesh.RefinementCircle(center2, radius2, max_area)
        dist_reg_1 = region1.distance_to_region(region2)
        dist_reg_2 = region2.distance_to_region(region1)

        desired_dist = lin.norm(translation) - radius - radius2

        nptest.assert_allclose(dist_reg_1, dist_reg_2, rtol=rtol, atol=atol)
        nptest.assert_allclose(dist_reg_1, desired_dist, rtol=rtol, atol=atol)
        # Also check distance to itself
        dist_reg_1_self = region1.distance_to_region(region1)
        nptest.assert_allclose(dist_reg_1_self, 0, atol=atol)


class TestManyRegionRefinement(unittest.TestCase):
    def test_empty(self):
        region = mesh.RefinementMany([])
        coords, trias = region.produce_mesh()
        self.assertEqual(coords, [])
        self.assertEqual(trias, [])
        self.assertAlmostEqual(region.distance_to_point([1, 2]), np.inf)

    def test_many_circles(self):
        centers = [(0, 0), (0, 10), (10, 0)]
        radii = [1, 2, 4]
        max_areas = [0.3, 0.8, 1.5]
        circles = []
        for i, center in enumerate(centers):
            circles.append(mesh.RefinementCircle(center, radii[i], max_areas[i]))

        region = mesh.RefinementMany(circles)

        coords, trias = region.produce_mesh()

        self.assertTrue(is_area_satisfied(coords, trias, max(max_areas)))
        self.assertTrue(is_angle_satisfied(coords, trias))

    def test_exception_thrown(self):
        centers = [(0, 0), (0, 10), (17, 0)]
        radii = [1, 10, 4]
        max_areas = [0.3, 0.8, 1.5]
        circles = []
        for i, center in enumerate(centers):
            circles.append(mesh.RefinementCircle(center, radii[i], max_areas[i]))

        region = mesh.RefinementMany(circles)
        with  self.assertRaises(NotImplementedError):
            region.produce_mesh()