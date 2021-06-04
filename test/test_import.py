import unittest
import numpy as np


class TestImports(unittest.TestCase):
    '''
    Test import of various packages, needed for this project
    '''

    def test_various_imports(self):
        import matplotlib
        import pandas


    def test_parallel_libs_import(self):
        import threading
        import queue

    def test_triangle_import(self):
        '''
        Original: https://github.com/drufat/triangle.git
        My: https://github.com/icemtel/triangle.git
        cd triangle
        python setup.py develop
        OR
        python setup.py install
        '''
        import triangle
        points = np.array([[0, 0], [0, 1], [0.5, 0.5], [1, 1], [1, 0]])  # sp.array([[0, 0], [0, 1], [1, 1], [1, 0]])
        tri_data = {'vertices': points}
        tri = triangle.triangulate(tri_data)

