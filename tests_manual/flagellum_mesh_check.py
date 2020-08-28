'''
Quick test functions in the file

Observed:
1. If points2=None, then we cannot run the meshing.

2. If we have input points on x axis - from 0 to 10 with a step of 1, then
   Mesh will create points on circumferences at points x=0.5..9.5;
   then at 0 and 10 there will be only 1 point - flagella tips.

3. Velocities are prescribed at nodes (will be later prescribed to element,
   by averaging velocities at each point of an element - when writing the input file).
   Values of velocity - medium between what should be prescribed at x = 0 and x = 1.
   Since the node of the mesh will be located at x=0.5, this makes sense.


Conclusion from fbem_simulations/playground/create_flagellum_arbitrary_normal_check.py:
!!! 4. Mesh gets rotated after changing phase of the flagellum.
'''
import numpy as np
import matplotlib.pyplot as plt
from mesh.shapes.Flagellum import prepareFlagella

radius = 0.1
nTheta = 4
a = np.array([1, 0, 0])
b = np.array([0, 1, 0])
points = [k * a for k in np.linspace(0, 10, 11)]
vels = [b * k ** 2 for k in np.linspace(0, 10, 11)]
points2 = [k * a + vels[k] for k in range(11)]
c, v, t = prepareFlagella(radius, points, points2, nTheta=nTheta)

print(c.shape, v.shape, t.shape)
array_to_print = v
for i, p in enumerate(points):
    print("Point:", p, "Velocity:", vels[i])
    print("x\t\tVelocity")
    if i < len(p) - 1:
        for j in range(nTheta):
            print(c[nTheta * i + j][0], v[nTheta * i + j], sep='\t')
    else:
        print(c[nTheta * i + 0][0], v[nTheta * i + 0], sep='\t')
        print(c[nTheta * i + 1][0], v[nTheta * i + 1], sep='\t')


from mpl_toolkits.mplot3d import Axes3D # for 3d plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

xs, ys, zs = np.array(points).transpose()
ax.scatter(xs, ys, zs)

xs, ys, zs = np.array(c).transpose()
ax.scatter(xs, ys, zs)
