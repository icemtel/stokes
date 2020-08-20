"""
This file is called by routine which creates mesh from nested dictionaries (convert.py).
"""

import numpy as np
from math import sin, cos, pi, sqrt
from scipy import spatial as scipy3D
from mesh import orient as orient


# ----- Main class -----

class Ellipsoid:  # used to be based on (Shape)
    def __init__(self, lengths=(1, 1, 1), axe1=(1, 0, 0), axe2=(0, 1, 0), grid=30):
        """
        an ellipoid at position position with principal axes axe1
        and axe2 with the lengths lengths.
        """
        A = getSpheroidA(lengths, axe1, axe2)
        # in Gary's code the position was taken from input, but the coordinates of Ellipsoid were not changed
        self.position = (0, 0, 0)
        (self.r, self.drdt, self.drdp) = map(lambda f: np.vectorize(f), spheroidFull(A))
        oldGrid = surfaceGrid(grid)
        self.grid = grid2numpyEllipsoid(oldGrid, self.r)

    # This code is not used in meshing, but maybe somewhere else??
    # def integrate(self, f):
    #     """
    #     I want f to be a function of cartesian coordinates!
    #     """
    #     prefactor_dA = self.r(self.grid[0], self.grid[1]) * numpy.sqrt(
    #         (self.r(self.grid[0], self.grid[1]) ** 2 + self.drdt(self.grid[0], self.grid[1]) ** 2) * numpy.sin(
    #             self.grid[0]) ** 2 + self.drdp(self.grid[0], self.grid[1]) ** 2)
    #     dAs = prefactor_dA * self.grid[2] * self.grid[3]
    #     fvec = numpy.vectorize(f)
    #     res = fvec(self.grid[4] + self.position[0], self.grid[5] + self.position[1],
    #                self.grid[6] + self.position[2]) * dAs
    #     return numpy.sum(res)
    #
    # def surfaceArea(self):
    #     return self.integrate(lambda x, y, z: 1)
    #
    # def integrateField(self, field):
    #     """
    #     a field is a vector function of cartesian coordinates
    #     """
    #     prefactor_dA = self.r(self.grid[0], self.grid[1]) * numpy.sqrt(
    #         (self.r(self.grid[0], self.grid[1]) ** 2 + self.drdt(self.grid[0], self.grid[1]) ** 2) * numpy.sin(
    #             self.grid[0]) ** 2 + self.drdp(self.grid[0], self.grid[1]) ** 2)
    #     dAs = prefactor_dA * self.grid[2] * self.grid[3]
    #     fvec = numpy.vectorize(f) #f=field? check
    #     res = fvec(self.grid[4] + self.position[0], self.grid[5] + self.position[1],
    #                self.grid[6] + self.position[2]) * dAs
    #     return (numpy.sum(res[0]), numpy.sum(res[1]), numpy.sum(res[2]))


def prepareEllipsoid(lengths=(1, 1, 1),
                     axe1=(1, 0, 0),
                     axe2=(0, 1, 0),
                     velocity=(0, 0, 0),
                     angular=(0, 0, 0),
                     grid=30):
    """
    Creates a mesh for an ellipsoid.
    Mesh will have grid^2 points, or grid^2 +1 if grid is an odd number.
    """
    ellipsoid = Ellipsoid(lengths=lengths, axe1=axe1, axe2=axe2, grid=grid)
    return prepareConvexShape(ellipsoid, velocity, angular)


def prepareConvexShape(shape, velocity, angular):
    """
    Triangulate the ellipsoid.
    Apply translational and angular velocities.
    """
    velocity = np.array(velocity)

    # coordinates
    coordinates = []
    for coord in zip(shape.grid[4], shape.grid[5], shape.grid[6]):
        coordinates.append(coord)

    # velocities
    origin = np.array(shape.position)
    velocities = []
    for v in coordinates:
        # vector to be rotated
        toBeRotated = np.array(v) - origin
        # rotated vector
        # rotated = rotate.rotateVector(toBeRotated, norm(angular), angular)
        veloFromAng = -np.cross(toBeRotated, angular)
        # velocity of the surface element
        velocities.append(veloFromAng + velocity)

    # triangulation
    triangulation = orient.orientateTriangulation(origin, coordinates, scipy3D.ConvexHull(coordinates).simplices)

    return (coordinates, velocities, triangulation)


# Some helper functions
# (1) Functions from GK's surfaceintegration.py
#

def xFromSphere(r, theta, phi):
    return r * sin(theta) * cos(phi)


def yFromSphere(r, theta, phi):
    return r * sin(phi) * sin(theta)


def zFromSphere(r, theta, phi):
    return r * cos(theta)


def cartesianFromSphere(r, theta, phi):
    return (xFromSphere(r, theta, phi)
            , yFromSphere(r, theta, phi)
            , zFromSphere(r, theta, phi))


def thetaDivision(n):
    return [pi / n * (i + 0.5) for i in range(n)]


def phiDivision(n):
    return [2 * pi / n * (i + 0.5) for i in range(n)]


def surfaceGrid(nTheta):
    """
    more homogeneous key on the surface than with thetaDivision
    and phiDivision. But: dPhi is variable!
    Therefore return a dict with values as keys_text and differences as values.
    """

    def phis(n):
        if n < nTheta / 2:
            res = 4 * n + 2
        else:
            res = (-4) * (n - nTheta) - 2
        return res

    res = {}
    for (t, counter) in zip(thetaDivision(nTheta), range(nTheta)):
        for p in phiDivision(phis(counter)):
            res[(t, p)] = (pi / nTheta, 2 * pi / phis(counter))
    return res


def grid2numpyEllipsoid(grid, shape):
    num = len(grid)
    thetas = np.zeros([num])
    phis = np.zeros([num])
    dthetas = np.zeros([num])
    dphis = np.zeros([num])
    xs = np.zeros([num])
    ys = np.zeros([num])
    zs = np.zeros([num])
    for (c, (t, p)) in zip(range(num), grid):
        (x, y, z) = cartesianFromSphere(shape(t, p), t, p)
        xs[c] = x
        ys[c] = y
        zs[c] = z
        thetas[c] = t
        phis[c] = p
        dthetas[c] = grid[(t, p)][0]
        dphis[c] = grid[(t, p)][1]
    return (thetas, phis, dthetas, dphis, xs, ys, zs)


# (2) from GK's shapes.py

def getSpheroidA(lengths, axe1, axe2):
    """
    construct matrix from two eigenvectors that should be orthogonal to each other
    (due to the interpretation of the values for an ellipse) and eigenvalues (which are
    interpreted as length for principle axes). The generated output can be used as
    input for the function spheroid and co.
    """
    from numpy import diag, array, cross, dot, transpose
    from scipy.linalg import inv, norm
    L = diag(1 / (array(lengths)) ** 2)
    axe3 = cross(axe1, axe2)
    axe2 = cross(axe1, axe3)  # if axe1 and axe2 are not orthogonal
    axe1 = array(axe1) / norm(axe1)
    axe2 = array(axe2) / norm(axe2)
    axe3 = array(axe3) / norm(axe3)
    Ph = array([axe1.tolist(), axe2.tolist(), axe3.tolist()])
    P = transpose(Ph)
    PInv = inv(P)
    return dot(dot(P, L), PInv)


def spheroid(A):
    """
    a general notation of a spheroid is x^T*A*x == 1. The eigenvector
    of A determine the orientation of the principle axis and the
    eigenvalues are the squares of the lengths of these axis.
    r was calculated using mathematica.
    """
    r1 = lambda t, p: sin(t) ** 2 * (
            A[0][0] * cos(p) ** 2 + (A[0][1] + A[1][0]) * sin(p) * cos(p) + A[1][1] * sin(p) ** 2)
    r2 = lambda t, p: sin(t) * cos(t) * ((A[0][2] + A[2][0]) * cos(p) + (A[1][2] + A[2][1]) * sin(p))
    r3 = lambda t, p: cos(t) ** 2 * A[2][2]
    return lambda t, p: 1 / sqrt(r1(t, p) + r2(t, p) + r3(t, p))


def DspheroidDt(A):
    """ derivatves of the shape function, used for integration """
    r1 = lambda t, p: -2 * cos(2 * t) * ((A[0][2] + A[2][0]) * cos(p) + (A[1][2] + A[2][1]) * sin(p))
    r2 = lambda t, p: (-1) * (
            A[0][0] + A[1][1] - 2 * A[2][2] + (A[0][0] - A[1][1]) * cos(2 * p) + (A[0][1] + A[1][0]) * sin(
        2 * p)) * sin(2 * t)
    r3 = lambda t, p: 4 * (
            A[2][2] * cos(t) ** 2 + cos(t) * ((A[0][2] + A[2][0]) * cos(p) + (A[1][2] + A[2][1]) * sin(p)) * sin(t))
    r4 = lambda t, p: 4 * (A[0][0] * cos(p) ** 2 + (A[0][1] + A[1][0]) * cos(p) * sin(p) + A[1][1] * sin(p) ** 2) * sin(
        t) ** 2
    return lambda t, p: (r1(t, p) + r2(t, p)) / sqrt(r3(t, p) + r4(t, p)) ** 3


def DspheroidDp(A):
    """ derivatves of the shape function, used for integration """
    r1 = lambda t, p: sin(t) * ((-(A[1][2] + A[2][1])) * cos(p) * cos(t) + (A[0][2] + A[2][0]) * cos(t) * sin(p))
    r2 = lambda t, p: ((A[0][1] + A[1][0]) * cos(2 * p) + (A[1][1] - A[0][0]) * sin(2 * p)) * sin(t) ** 2
    r3 = lambda t, p: 2 * (
            A[2][2] * cos(t) ** 2 + cos(t) * ((A[0][2] + A[2][0]) * cos(p) + (A[1][2] + A[2][1]) * sin(p)) * sin(t))
    r4 = lambda t, p: 2 * (A[0][0] * cos(p) ** 2 + (A[0][1] + A[1][0]) * cos(p) * sin(p) + A[1][1] * sin(p) ** 2) * sin(
        t) ** 2
    return lambda t, p: (r1(t, p) + r2(t, p)) / sqrt(r3(t, p) + r4(t, p)) ** 3


def spheroidFull(A):
    return [f(A) for f in [spheroid, DspheroidDt, DspheroidDp]]
