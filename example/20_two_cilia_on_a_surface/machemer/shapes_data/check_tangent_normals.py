'''
- tangent is not following the finite different of points very well (but the same happens with original data..)
'''
import numpy as np

tx = np.loadtxt('tx-data')
ty = np.loadtxt('ty-data')
tz = np.loadtxt('tz-data')
nx = np.loadtxt('nx-data')
ny = np.loadtxt('ny-data')
nz = np.loadtxt('nz-data')

tt = np.array([tx, ty, tz]).swapaxes(0, 2).swapaxes(0, 1)
nn = np.array([nx, ny, nz]).swapaxes(0, 2).swapaxes(0, 1)

for phase in range(20):
    for ix in range(121):
        t = tt[phase, ix]
        n = nn[phase, ix]
        # Check orthogonality
        if not np.allclose(t.dot(n), 0):
            print(t.dot(n))
            raise ValueError

## Is tangent in the right direciton?
x = np.loadtxt('x-data')
y = np.loadtxt('y-data')
z = np.loadtxt('z-data')
rr = np.array([x, y, z]).swapaxes(0, 2).swapaxes(0, 1)


for phase in range(1, 20):
    for ix in range(121):
        t = tt[phase, ix]
        r1 = rr[phase, ix]
        r0 = rr[phase - 1, ix]
        dr = r1 - r0
        dr /= np.linalg.norm(dr)  # normalize

        # Check that almost tangential
        if dr.dot(t) < 0:
            print(phase, ix, dr.dot(t))
            raise ValueError
