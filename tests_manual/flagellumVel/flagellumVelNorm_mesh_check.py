'''
Flagellum with specified rate of cange of normal vector:
Checked:
- Rotational part scales as r
- Rotation in counter-clock-wise direction => rotational velocity of a point above x=0 - negative; below - positive.
  Values match with the calculations on paper.
- Sum of the velocities added is equal to zero.
'''
import scipy as sp
from mesh.shapes.FlagellumVelNorm import prepareFlagellaVelNorm

radius = 0.1
nTheta = 4
n_L = 11
L = 10
a = sp.array([1, 0, 0])
b = sp.array([0, 1, 0])
points = [k * a for k in sp.linspace(0, L, n_L)]
# Rotation around 0
angular_velocity = 1
angle = 0
#vels = [angular_velocity * length * (b * sp.cos(angle) - a * sp.sin(angle)) for length in sp.linspace(0, L, n_L)]
vels = [0 * a for length in sp.linspace(0, L, n_L)]
tangents = [a for p in points]
normals = [b for p in points]
dndt = [- angular_velocity * t for t in tangents]


c, v, t = prepareFlagellaVelNorm(points, vels, tangents, normals, dndt, radius, nTheta=nTheta)

print(c.shape, v.shape, t.shape)
array_to_print = v
for i, p in enumerate(points[1:-1]):
    print("Point:", p, "Velocity:", vels[i])
    print("x\t\t\tVelocity")
    le = nTheta * i + 1
    for j in range(nTheta):
        print(c[le + j], v[le + j], sep='\t')

# The first and the last points
print("Point:", points[0], "Velocity:", vels[0])
print("x\t\t\tVelocity")
print(c[0], v[0], sep='\t')
print("Point:", points[-1], "Velocity:", vels[-1])
print("x\t\t\tVelocity")
print(c[-1], v[-1], sep='\t')


## Plot nodes
# import quick
#
# with quick.Plot(projection='3d') as qp:
#     xs, ys, zs = sp.array(points).transpose()
#     qp.scatter(xs, ys, zs)
#
#     xs, ys, zs = sp.array(c).transpose()
#     qp.scatter(xs, ys, zs)
#


# Sum of material frame rotation velocities should be zero:
print(sp.sum(v,axis=0)) # - Passed

