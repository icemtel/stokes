"""
This file is called by routine which creates mesh from nested dictionaries (convert.py).
"""

import numpy as np
from scipy import spatial as scipy3D
import mesh.orient as orient


def preparePlane(p0=(-1, -1, -1),
                 p1=(1, 1, 1),
                 p2=(0, 0, 1),
                 width=1,
                 grid1=3,
                 grid2=3,
                 centers=None):
    """
    One side of the plane is defined by 3 points: p0,p1,p2, the last point is p0 + (p1 - p0) + (p2 - p0).
    The other side is parallel to the other, the distance is equal to *width*.
    In total mesh will have 2*(grid1+1)*(grid2+1) nodes.
    Centers - list of coordinates, where the mesh will be condensed.
    WARNING: at some distance from the center, mesh will be sparsed.
    """
    if grid1 == 0 or grid2==0:
        raise ValueError('grid parameter has to be an integer > 0')
    p0 = np.array(p0)

    dp1 = np.array(p1) - p0
    dp2 = np.array(p2) - p0
    dp3 = np.cross(dp1, dp2)
    dp3 = dp3 / np.linalg.norm(dp3) * width

    origin = p0 + 0.5 * (dp1 + dp2 + dp3)
    c = np.zeros((2 * (grid1 + 1) * (grid2 + 1), 3))  # coordinates
    v = np.zeros((2 * (grid1 + 1) * (grid2 + 1), 3))  # velocities
    fI1 = lambda n, m: n * (grid2 + 1) + m  # The first part (lower part) of the plane numbering
    fI2 = lambda n, m: n * (grid2 + 1) + m + (grid1 + 1) * (grid2 + 1)  # The upper plane numbering
    for i in range(grid1 + 1):
        alpha = i / grid1
        for j in range(grid2 + 1):
            beta = j / grid2

            c[fI1(i, j)] = p0 + alpha * dp1 + beta * dp2
            c[fI2(i, j)] = p0 + alpha * dp1 + beta * dp2 + dp3
            # v[fI1(i, j)] = velocityfield(c[fI1(i, j)][0],
            #               c[fI1(i, j)][1],
            #               c[fI1(i, j)][2])
            # v[fI2(i, j)] = velocityfield(c[fI2(i, j)][0],
            #               c[fI2(i, j)][1],
            #               c[fI2(i, j)][2])
    t = []  # triangulation
    for i in range(grid1):  # Combine nearby nodes into triangles
        for j in range(grid2):
            t.append([fI1(i, j), fI1(i + 1, j), fI1(i + 1, j + 1)])
            t.append([fI2(i, j), fI2(i + 1, j + 1), fI2(i + 1, j)])
            t.append([fI1(i, j), fI1(i + 1, j + 1), fI1(i, j + 1)])
            t.append([fI2(i, j), fI2(i, j + 1), fI2(i + 1, j + 1)])
    for i in range(grid1):  # Connect upper and lower plane
        t.append([fI1(i, grid2), fI2(i + 1, grid2), fI1(i + 1, grid2)])
        t.append([fI1(i, grid2), fI2(i, grid2), fI2(i + 1, grid2)])
        t.append([fI1(i + 1, 0), fI1(i, 0), fI2(i, 0)])
        t.append([fI1(i + 1, 0), fI2(i + 1, 0), fI2(i, 0)])
    for j in range(grid2):  # Connect upper and lower plane
        t.append([fI1(grid1, j + 1), fI1(grid1, j), fI2(grid1, j)])
        t.append([fI1(grid1, j + 1), fI2(grid1, j), fI2(grid1, j + 1)])
        t.append([fI1(0, j), fI2(0, j + 1), fI1(0, j + 1)])
        t.append([fI1(0, j), fI2(0, j), fI2(0, j + 1)])
    # Apply 'centers'
    dmax = 20  # The maximum dsitance from the point where the nodes positions will be changed
    alpha = lambda d: 0.7 * (d / dmax) + 0.3
    if centers is not None:
        for center in centers:
            for i in range(1, grid1):  # Iterate over all the grid points, except the first and the last
                for j in range(1, grid2):  # Iterate over all the grid points, except the first and the last
                    dij = c[fI1(i, j)] - center
                    dij_norm = np.linalg.norm(dij)
                    if dij_norm < dmax:
                        c[fI1(i, j)] = alpha(dij_norm) * dij + center
                    dij = c[fI2(i, j)] - center
                    dij_norm = np.linalg.norm(dij)
                    if dij_norm < dmax:
                        c[fI2(i, j)] = alpha(dij_norm) * dij + center
    t = orient.orientateTriangulation(origin, c, t)

    c = np.array(c)
    v = np.array(v)
    t = np.array(t)
    return (c, v, t)


def prepareCuboid(p0=(0, 0, 0),
                  p1=(0, 1, 0),
                  p2=(0, 0, 1),
                  p3=(1, 0, 0),
                  grid1=3,
                  grid2=3,
                  grid3=3,
                  velocityfield=lambda x, y, z: (0, 0, 0),
                  type='cuboid'):
    '''
    Each side of the cuboid will have (grid_k +1) * (grid_j +1) nodes.
    Despite the name, can be a parallelepiped, not just a rectangular cuboid.
    '''
    if type != 'cuboid':
        raise TypeError
    if grid1 == 0 or grid2==0 or grid3 ==0:
        raise ValueError('grid parameter has to be an integer > 0')
    p0 = np.array(p0)
    dp1 = np.array(p1) - p0
    dp2 = np.array(p2) - p0
    dp3 = np.array(p3) - p0
    origin = p0 + 0.5 * (dp1 + dp2 + dp3)

    coords = []
    for i in range(grid1 + 1):
        alpha = i / float(grid1)
        for j in range(grid2 + 1):
            beta = j / float(grid2)
            coords.append(p0 + alpha * dp1 + beta * dp2)
            coords.append(p0 + alpha * dp1 + beta * dp2 + dp3)
    for i in range(grid1 + 1):
        alpha = i / float(grid1)
        for j in range(grid3):
            beta = (j + 1) / float(grid3)
            coords.append(p0 + alpha * dp1 + beta * dp3)
            coords.append(p0 + alpha * dp1 + beta * dp3 + dp2)
    for i in range(grid3):
        alpha = (i + 1) / float(grid3)
        for j in range(grid2):
            beta = (j + 1) / float(grid2)
            coords.append(p0 + alpha * dp3 + beta * dp2)
            coords.append(p0 + alpha * dp3 + beta * dp2 + dp1)

    v = []
    for c in coords:
        v.append(velocityfield(c[0], c[1], c[2]))
    d = scipy3D.Delaunay(coords)
    t = orient.orientateTriangulation(origin, coords, d.convex_hull)

    c = np.array(coords)
    v = np.array(v)
    t = np.array(t)
    return (c, v, t)


if __name__ == "__main__":
    '''
    Make some plots
    '''
    import matplotlib.pyplot as plt

    p0=(0, 0, 0)
    p1 = (0, 1, 0)
    p2 = (0, 0, 1)
    p3 = (1, 0, 0)
    grid1 = 3
    grid2 = 3
    grid3 = 3

    type = 'cuboid'
    c, v, t = prepareCuboid(p0=p0,
                  p1=p1,
                  p2=p2,
                  p3=p3,
                  grid1=grid1,
                  grid2=grid2,
                  grid3=grid3,
                  velocityfield=lambda x, y, z: (0, 0, 0),
                  type=type)

    # Plot
    x, y, z = c.transpose()
    plt.plot(x, y, z, 'o')
    for tria in t:
        for id1, id2 in zip(tria, tria[1:]):
            x, y, z = np.array([c[id1], c[id2]]).transpose()
            plt.plot(x, y, z, color='blue')
        x, y, z = np.array([c[tria[0]], c[tria[-1]]]).transpose()
        plt.plot(x, y, z, color='blue')
    plt.show()