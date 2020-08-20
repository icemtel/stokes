'''

'''
import scipy as sp
from mesh.shapes.FlagellumVel import prepareFlagellaVel

radius = 0.1
nTheta = 4
n_L = 11
L = 10
a = sp.array([1, 0, 0])
b = sp.array([0, 1, 0])
points = [k * a for k in sp.linspace(0, L, n_L)]
vels = [ b * k ** 2 for k in sp.linspace(0, L, n_L)]
tangents = [a for p in points]
normals = [b for p in points]


c, v, t = prepareFlagellaVel(points, vels, tangents, normals, radius, nTheta=nTheta)

print(c.shape, v.shape, t.shape)
array_to_print = v
for i, p in enumerate(points[1:-1]):
    print("Point:", p, "Velocity:", vels[i])
    print("x\t\t\tVelocity")
    for j in range(nTheta):
        print(c[nTheta * i + j], v[nTheta * i + j], sep='\t')

# The first and the last points
print("Point:", points[0], "Velocity:", vels[0])
print("x\t\t\tVelocity")
print(c[0], v[0], sep='\t')
print("Point:", points[-1], "Velocity:", vels[-1])
print("x\t\t\tVelocity")
print(c[-1], v[-1], sep='\t')

import quick

with quick.Plot(projection='3d') as qp:
    xs, ys, zs = sp.array(points).transpose()
    qp.scatter(xs, ys, zs)

    xs, ys, zs = sp.array(c).transpose()
    qp.scatter(xs, ys, zs)
