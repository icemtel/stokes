'''
Flagellum updated version.
 - Keep track of material frame when making nodes on the circles.
 - Calculate velocities using finite difference. Take into account rotation of material frame.
 - Nodes on the circle are created around given centerline points
 (before they were created right in the middle of two given points)
'''

import numpy as np
from scipy.linalg import norm
import mesh.rotate as rotate


def skip(iterable, at_start=0, at_end=0):
    # https://stackoverflow.com/a/18836614/5322720
    import itertools
    it = iter(iterable)
    it = itertools.islice(it, at_start, None)
    it, it1 = itertools.tee(it)
    it1 = itertools.islice(it1, at_end, None)
    return (next(it) for _ in it1)


def circleVectors2(center, normal, tangent, nTheta, radius, offset_angle=0):
    """
    Don't shift the center in tangent direction like in the `circleVectors`
    """
    res = []
    rotated = rotate.rotateVector(normal, offset_angle, tangent)
    angle = 2 * np.pi / nTheta
    for n in range(nTheta):
        res.append(center + rotated * radius)
        rotated = rotate.rotateVector(rotated, angle, tangent)
    return res


class Flagellum2:
    def __init__(self, points, tangents, normals, radius, nTheta, points_next, tangents_next, normals_next, dt):
        self.firstPoint = points[0]
        self.lastPoint = points[-1]
        # Array with coordinates; fill with nans
        self.surfaceCoords = np.empty((len(points) - 2, nTheta, 3))
        self.surfaceCoords.fill(np.nan)
        # Array with velocities; fill with nans
        self.surfaceVelocities = np.copy(self.surfaceCoords)
        # Make sure tangents and normals are normalized:
        # tangents = [sp.array(t) / norm(t) for t in tangents] # - Already normalized in rotation function
        normals = [np.array(n) / norm(n) for n in normals]
        # Skip the first and the last points - flagella tips
        iterate_over = skip(zip(points, tangents, normals, points_next, tangents_next, normals_next),
                            at_start=1, at_end=1)
        # Run a loop to fill the surfaceParametrization array with surface coordinates
        # Finite difference to find velocities
        # c - point on the centerline; t - tangent, n - normal
        for i, (c, t, n, c_next, t_next, n_next) in enumerate(iterate_over):
            circle_coords = circleVectors2(c, n, t, nTheta, radius)
            circle_coords_next = circleVectors2(c_next, n_next, t_next, nTheta, radius)
            for j, (coord, coord_next) in enumerate(zip(circle_coords, circle_coords_next)):
                self.surfaceCoords[i, j] = coord
                self.surfaceVelocities[i, j] = (coord_next - coord) / dt

    def triangulate(self):
        def get2dIndex(point):
            for (c, p) in zip(range(len(twoDpoints)), twoDpoints):
                if p[0] == point[0] and p[1] == point[1]:
                    return c
            print(c, p, point)
            raise RuntimeError('bad result from get2dIndex!')

        (lineElements, circleElements, _) = self.surfaceCoords.shape
        twoDpoints = [(i, j) for i in range(lineElements) for j in range(circleElements)]
        # the following part of twoDpoints must be at the end of the list
        # so that the 'replace' dictionary, that means the values to be replaced
        # are the highest index values. This ensures that the triangulation contains
        # indices from 1 to index_max.
        twoDpoints += [(i, circleElements) for i in range(lineElements)]

        tri = []
        for (i, j) in [(i, j) for i in range(lineElements - 1) for j in range(circleElements)]:
            tri.append((get2dIndex((i, j)), get2dIndex((i + 1, j)), get2dIndex((i, j + 1))))
            tri.append((get2dIndex((i + 1, j)), get2dIndex((i + 1, j + 1)), get2dIndex((i, j + 1))))
        res = []

        # create replace list
        replace = {}
        for (i, p) in zip(range(len(twoDpoints)), twoDpoints):

            if p[1] == circleElements:
                # get the index of p[0] in tri.points
                for (j, ph) in zip(range(len(twoDpoints)), twoDpoints):
                    if ph[0] == p[0] and ph[1] == 0:
                        replace[i] = j

        # replace
        for s in tri:
            (sx, sy, sz) = s
            for r in replace:
                if r == sx:
                    sx = replace[r]
                elif r == sy:
                    sy = replace[r]
                elif r == sz:
                    sz = replace[r]
            res.append((sx, sy, sz))
        return res


def prepareFlagella2(points, tangents, normals, radius, nTheta, points_next, tangents_next, normals_next, dt,
                     type='flagellum2'):
    """
    New version - which respects material frame.
    :param points: list of centerline points [[x11,x12,x13],[x21,x22,x23]..]
    :param vels: list of point velocities [[v11,v12,v13],[v21,v22,v23]..]
    :param tangents: list of tangent vectors in each point
    :param normals:  list of normal vectors; azimuth grid points will be first placed in the direction where normal points
    Each of tangent and normal vectors will be normalized.
    :param nTheta: Number of azimuth grid points
    :return:
    """
    if type != 'flagellum2':
        raise TypeError
    # Transform input to the list of points, each point is represented by np.array
    points = list(map(lambda v: np.array(v), points))
    tangents = list(map(lambda c: np.array(c), tangents))
    normals = list(map(lambda c: np.array(c), normals))
    points_next = list(map(lambda v: np.array(v), points_next))
    tangents_next = list(map(lambda c: np.array(c), tangents_next))
    normals_next = list(map(lambda c: np.array(c), normals_next))

    flagella = Flagellum2(points, tangents, normals, radius, nTheta, points_next, tangents_next, normals_next, dt)
    ## Start with the first tip
    coordinates = [points[0]]
    tip_velocity = (points_next[0] - points[0]) / dt
    velocities = [tip_velocity]
    (lineElements, circleElements, coords) = flagella.surfaceCoords.shape
    for le in range(lineElements):
        for ce in range(circleElements):
            coordinates.append(flagella.surfaceCoords[le, ce])
            velocities.append((flagella.surfaceVelocities[le, ce]))  # To account for the first point already added

    ## Append flagellum second tip
    coordinates.append(points[-1])
    velocities.append((points_next[-1]  - points[-1]) / dt)

    # Triangulate
    triangulation = []
    # 1. The first tip
    # the first point connects to the first circleElements of coordinates
    # be careful with orientation
    tip_idx = 0
    circle_idxs = np.array(range(circleElements)) + 1
    for (i2, i3) in zip(circle_idxs[:-1], circle_idxs[1:]):
        triangulation.append((tip_idx, i2, i3))
    triangulation.append((tip_idx, circle_idxs[-1], circle_idxs[0]))

    # 2. Add intermediate triangles
    triangulation0 = flagella.triangulate()
    triangulation0 = [[idx + 1 for idx in tria] for tria in triangulation0] # +1 Since we added the tip in the beginning
    triangulation += triangulation0

    # 3. Add the second tip
    # the last point connects to the last circleElements of coordinates - 2
    tip_idx = lineElements * circleElements + 1
    circle_idxs = [i + 1 + (lineElements - 1) * circleElements for i in range(circleElements)]
    for (i2, i3) in zip(circle_idxs[:-1], circle_idxs[1:]):
        triangulation.append((tip_idx, i3, i2))
    triangulation.append((tip_idx, circle_idxs[0], circle_idxs[-1]))

    c = np.array(coordinates)
    v = np.array(velocities)
    t = np.array(triangulation, dtype=np.uint)
    return (c, v, t)
