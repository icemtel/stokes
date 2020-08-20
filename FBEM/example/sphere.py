import mesh
import FBEM

folder = 'data/sphere'

position = (0, 0, 0)
radius = 1
velocity = (2, 0, 0)
angular = (0, 0, 3)
sphere_grid = 4 # Mesh consisting of 4x4 nodes
#---
sphere = mesh.sphere_create('sphere', position, radius, velocity, angular, sphere_grid)

FBEM.run(sphere, folder)
