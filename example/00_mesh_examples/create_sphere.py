'''
'''
import mesh


position = (0, 0, 0)
radius = 1
velocity = (2, 0, 0)
angular = (0, 0, 3)
sphere_grid = 16 # Mesh consisting of 4x4 nodes

# Create mesh
sphere = mesh.sphere_create('sphere', position, radius, velocity, angular, sphere_grid)
tri = mesh.triangulate_system(sphere)

## Visualize
import mesh.plot.trimesh_viewer as mplot # visualize

m = mplot.triangulation_to_trimesh(tri) # class of TriMesh, suitable for plotting
m.show() # visualize - 3D