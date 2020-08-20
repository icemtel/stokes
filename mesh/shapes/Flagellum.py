"""
This file is called by routine which creates mesh from nested dictionaries (convert.py).

Some insight on how prepareFlagella works - in flagellum_mesh_check.py

Preferred to use Flagellum2 or FlagellumVel or FlagellumVelNorm
"""

import mesh.rotate as rotate
import copy
import numpy as np  # import array, zeros, pi, dot, cross, arccos, arcsin, zeros_like
from scipy.linalg import norm


def circleVectors(position, normal, tangent, number, radius):
    """
    a circle with radius, consisting of number vectors at position
    around tangent axis. Start vector is normal.
    !!The circle center is shifted by 1/2 of tangent
    """
    res = []
    rotated = copy.deepcopy(normal)
    angle = 2 * np.pi / number
    for n in range(number):
        rotated = rotate.rotateVector(rotated, angle, tangent)
        res.append(position + 0.5 * tangent + rotated * radius)
    return res


def arbitraryNormalFromTangent(tangent):
    """ having a tangent vector, return some normal vector """
    normal = np.array([1, 1, 1.0])  # If I remove .0 -> tests fail ?!
    (tx, ty, tz) = tangent
    if tx == 0 and ty == 0:
        normal[2] = 0
    elif tx == 0 and tz == 0:
        normal[1] = 0
    elif ty == 0 and tz == 0:
        normal[0] = 0
    elif tx == 0:
        normal[1] = -tz * normal[2] / ty
    elif ty == 0:
        normal[0] = -tz * normal[2] / tx
    elif tz == 0:
        normal[0] = -ty * normal[1] / tx
    else:
        normal[0] = (ty * normal[1] + tz * normal[2]) / (-tx)
    return normal / norm(normal)


class Flagellum:
    """
    GK:
    after intialization of the flagella object, it contains
    the property surfaceParametrization. It is a matrix
    with position vectors as entries. Its indices can be used
    to automatically (via scipy.spatial.Delaunay) construct
    the triangulation.
    AS: original function is in klint_lib/triangulation.py
    """

    def __init__(self, radius, points, nTheta=5):
        self.firstPoint = points[0]
        self.lastPoint = points[-1]
        # Run a loop to fill the surfaceParametrization array with surface coordinates
        self.surfaceParametrization = np.zeros((len(points) - 1, nTheta, 3))
        # AS: next line output -> list of points, each point is represented by np.array
        points = list(map(lambda v: np.array(v), points))
        # determine the first normal vector
        tangent = points[1] - points[0]
        tangent_normed = tangent / norm(tangent)
        normal = arbitraryNormalFromTangent(tangent)
        for (i, p) in zip(range(len(points) - 1), points):
            # get all points around p
            for (j, circleVector) in zip(range(nTheta), circleVectors(p, normal, tangent, nTheta, radius)):
                self.surfaceParametrization[i, j] = circleVector
            if i + 2 == len(points):
                break
            # adjust tangent and normal: project old normal onto orthogonal plane.
            new_tangent = points[i + 2] - points[i + 1]
            new_tangent_normed = new_tangent / norm(new_tangent)
            # Calculate cross product -> find a rotation axis (not normalized)
            rot_axis = np.cross(tangent_normed, new_tangent_normed)
            # Get a rotation angle
            angle = np.arccos(np.dot(tangent_normed, new_tangent_normed))
            normal = rotate.rotateVector(normal, angle, rot_axis)

            tangent = new_tangent
            tangent_normed = new_tangent_normed
            ''' AS: code before fixing a bug (division by zero if norm(rot_vec) == 0)
            # + some of my comments
            tangent = tangent / norm(tangent)
            new_tangent = points[i + 2] - points[i + 1]
            rot_vec = cross(tangent, new_tangent / norm(new_tangent))
            angle = arccos(dot(tangent, new_tangent / norm(new_tangent)))
            rot_vec = rot_vec / norm(rot_vec) * angle

            normal = dot(rotate.axis2matrix(rot_vec), normal) # - can be dont with rotateVector function 
            normal = normal / norm(normal) # - not neseccery 

            tangent = new_tangent
            '''

    def triangulate(self):
        def get2dIndex(point):
            for (c, p) in zip(range(len(twoDpoints)), twoDpoints):
                if p[0] == point[0] and p[1] == point[1]:
                    return c
            print(c, p, point)
            raise RuntimeError('bad result from get2dIndex!')

        (lineElements, circleElements, coordinates) = self.surfaceParametrization.shape
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

        # a list of points is needed, so that simplices
        # contains indices of them
        self.surfacePoints = []
        for p in twoDpoints:
            try:
                self.surfacePoints.append(self.surfaceParametrization[p[0], p[1]])
            except:
                continue

        self.simplices = res
        self.points = twoDpoints
        return res

    # def triangulateOld(self): TODO: remove this code if not needed
    #     """ surface triangulation. """
    #     (lineElements, circleElements, coordinates) = self.surfaceParametrization.shape
    #     twoDpoints = [(i, j) for i in range(lineElements) for j in range(circleElements)]
    #     twoDpoints += [(i, circleElements) for i in range(lineElements)]
    #    import scipy.spatial as scipy3D
    #     # scipy.spatial.delaunay_plot_2d(tri)
    #     res = []
    #
    #     # create replace list
    #     replace = {}
    #     for (i, p) in zip(range(len(tri.points)), tri.points):
    #
    #         if p[1] == circleElements:
    #             # get the index of p[0] in tri.points
    #             for (j, ph) in zip(range(len(tri.points)), tri.points):
    #                 if ph[0] == p[0] and ph[1] == 0:
    #                     replace[i] = j
    #
    #     # replace
    #     for s in tri.simplices:
    #         (sx, sy, sz) = s
    #         for r in replace:
    #             if r == sx:
    #                 sx = replace[r]
    #             elif r == sy:
    #                 sy = replace[r]
    #             elif r == sz:
    #                 sz = replace[r]
    #         res.append((sx, sy, sz))
    #
    #     # a list of points is needed, so that simplices
    #     # contains indices of them
    #     self.surfacePoints = []
    #     for p in tri.points:
    #         try:
    #             self.surfacePoints.append(self.surfaceParametrization[p[0], p[1]])
    #         except:
    #             continue
    #
    #     self.points = tri.points
    #     self.simplices = res
    #
    #     return res
    #


def prepareFlagella(radius,
                    points1,
                    points2=None,
                    nTheta=6,
                    dt=1):
    """
    a flagella is represented as a list of points.
    given two such flagella allows us to compute the velocity
    at each point.
    Output: coordinates, velocities, and triangulation - in 'convert.py' will be transformed to scipy arrays
    """
    # TODO: Prescribe velocities instead of points2
    # TODO: And change meshProductionRule2Mesh, so that it can take optional arguments
    points1 = list(map(lambda c: np.array(c), points1))
    points2 = list(map(lambda c: np.array(c), points2))
    flagella = Flagellum(radius, points1, nTheta)
    coordinates = []
    velocities = []
    (lineElements, circleElements, coords) = flagella.surfaceParametrization.shape
    for le in range(lineElements):
        for ce in range(circleElements):
            coordinates.append(flagella.surfaceParametrization[le, ce])
            velocities.append(0.5 / dt * (points2[le] - points1[le] + points2[le + 1] - points1[le + 1]))

    triangulation = flagella.triangulate()

    ### take into account the first and last point
    coordinates.append(points1[0])
    coordinates.append(points1[-1])
    velocities.append((points2[0] - points1[0]) / dt)
    velocities.append((points2[-1] - points1[-1]) / dt)

    # the first point connects to the first circleElements of coordinates
    # be careful with orientation
    point1Index = lineElements * circleElements
    someIndices = list(range(circleElements))
    for (i2, i3) in zip(someIndices[:-1], someIndices[1:]):
        triangulation.append((point1Index, i2, i3))
    triangulation.append((point1Index, someIndices[-1], someIndices[0]))

    # the last point connects to the last circleElements of coordinates - 2
    point2Index = point1Index + 1
    someIndices = [i + (lineElements - 1) * circleElements for i in range(circleElements)]
    for (i2, i3) in zip(someIndices[:-1], someIndices[1:]):
        triangulation.append((point2Index, i3, i2))
    triangulation.append((point2Index, someIndices[0], someIndices[-1]))

    c = np.array(coordinates)
    v = np.array(velocities)
    t = np.array(triangulation, dtype=np.uint)
    return (c, v, t)