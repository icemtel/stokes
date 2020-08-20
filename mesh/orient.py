'''

'''
import numpy as np


def check_orientation(origin, points):
    '''
    *origin* is a point inside a (convex) shape
    Meaning of orientation:
    - look from origin to the triangle plane
    - return True if the triangle points are oriented counter-clockwise, returns True (orientation is suitable for FBEM)
    :origin: a reference point to check orinetation
    :points: coordinates of a triangle: array of 3 points, each is a 3D point
    '''
    origin = np.array(origin)
    [p1, p2, p3] = [np.array(point) for point in points]
    v12 = p1 - p2
    v32 = p3 - p2
    normal = np.cross(v12, v32)
    orientation = p1 + p2 + p3 - 3 * origin
    sign = np.dot(orientation, normal)
    if sign > 0:
        return True
    elif sign < 0:
        return False
    else:
        raise ValueError("Origin is in the triagnle plane")

def orientate(origin, points, triangle):
    """
    Check orientation, fix it if it is wrong.
    """
    if not check_orientation(origin, points):
        triangle = (triangle[0], triangle[2], triangle[1])
    return triangle


def orientateTriangulation(origin, points, triangulation):
    '''
    Fix orientation in triangles in a triangulation array (array of triangle indices).
    '''
    triangulationH = []
    for tri in triangulation:
        triH = orientate(origin, [points[tri[0]], points[tri[1]], points[tri[2]]], tri)
        triangulationH.append(triH)
    return triangulationH


if __name__ == '__main__':
    # Tests

    origin = np.array([0,0,1])
    points = np.array([[1,0,0], [0,1,0], [0,0,0]])
    print(check_orientation(origin, points)) # OK: True
