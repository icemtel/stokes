'''

'''
import scipy as sp
import mesh
import FBEM
import plot3D

folder = 'data/flagellum2'
radius = 1
nTheta = 4
n_L = 11
L = 10
a = sp.array([1, 0, 0])
b = sp.array([0, 1, 0])
points = [k * a for k in sp.linspace(0, L, n_L)]
vels = [ b * k ** 2 for k in sp.linspace(0, L, n_L)]
tangents = [a for p in points]
normals = [b for p in points]


system = mesh.flagellum_vel_create('flag', points, vels, tangents, normals, radius, azimuth_grid=nTheta)

FBEM.run(system, folder)

plot3D.MeshViewer(folder)

#
# import quick
#
# with quick.Plot(projection='3d') as qp:
#     xs, ys, zs = sp.array(points).transpose()
#     qp.scatter(xs, ys, zs)
#
#     xs, ys, zs = sp.array(c).transpose()
#     qp.scatter(xs, ys, zs)
