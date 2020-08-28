'''
Solve stokes equation for a moving sphere
- In practical applications the grid must be denser
'''
import mesh
import FBEM

folder = 'data/sphere/'

position = (0, 0, 0)
radius = 1
velocity = (2, 0, 0)
angular = (0, 0, 3)
sphere_grid = 4 # Mesh consisting of 4x4 nodes
#---
sphere = mesh.sphere_create('sphere', position, radius, velocity, angular, sphere_grid)

FBEM.run(sphere, folder) # Solve Stokes equation. output is written to a file


# Read triangulation from file
coords, trias = FBEM.read_all_triangulation_input(folder + 'input.dat')
# Alternatively, create triangulation with mesh package
#tri = mesh.triangulate_system(sphere) # class with coordinates and triangulation (list of triangles)
# trias = tri.triangulation
# coords = tri.coordinates

## Visualize triangulation
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d # 3d visualization

x = coords[:,0]
y = coords[:,1]
z = coords[:,2]

ax = plt.axes(projection='3d')
ax.plot_trisurf(x, y, z, triangles=trias,
                cmap='viridis', linewidths=0.2);

ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1);
plt.show()