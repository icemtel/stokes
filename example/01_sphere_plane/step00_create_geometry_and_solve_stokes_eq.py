'''
Solve a system of a moving sphere and a no-slip wall
'''
import mesh
import FBEM

folder = 'data/sphere_plane'

# Sphere parameters
sphere_position = (0, 0, 5)
radius = 1
velocity = (2, 0, 0)
angular = (0, 0, 3)
sphere_grid = 4  # Mesh consisting on 4x4 nodes
# Plane parameters
plane_position = (0,0,0)
plane_radius = 5 # Radius of the plane. Shape - circular
width = 1
max_area = 2 # max area of elements on the plane

sphere = mesh.sphere_create('sphere', sphere_position, radius, velocity, angular, sphere_grid)
plane = mesh.disk_create('plane', plane_radius, width, max_area, position=plane_position)

system = mesh.join_systems(sphere, plane)

FBEM.run(system, folder)
