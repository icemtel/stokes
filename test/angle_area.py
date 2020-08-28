import numpy as np
from scipy import linalg as lin

from FBEM import triangleArea


def get_triangle_area(tria, coords):
    xy1, xy2, xy3 = [coords[id] for id in tria]
    return triangleArea(xy1, xy2, xy3)


def get_cosine(v1, v2):
    return np.dot(v1, v2) / (lin.norm(v1) * lin.norm(v2))


def is_angle_satisfied(coords, trias, min_angle=20 * np.pi / 180):
    max_angle = np.pi - 2 * min_angle
    for tria in trias:
        tria_coords = []  # coordinates of triangle
        for i in range(3):
            tria_coords.append(coords[tria[i]])
        vectors = []  # Vectors between triangle points
        for i in range(3):
            vectors.append(tria_coords[(i + 1) % 3] - tria_coords[i])
        cosines = []
        for i in range(3):
            cosine = get_cosine(vectors[i], -vectors[(i + 1) % 3])  # cosine of triangle angle
            cosines.append(cosine)
        for cos in cosines:
            if cos > np.cos(min_angle):
                return False
    return True


def is_area_satisfied(coords, trias, max_area):
    '''
    True if all triangle areas are smaller than maximum area, otherwise False.
    '''
    for tria in trias:
        area = get_triangle_area(tria, coords)
        if area > max_area:
            return False
    return True