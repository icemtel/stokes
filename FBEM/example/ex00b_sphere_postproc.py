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


res = FBEM.extract_all_data(folder) # ResData class

velocities = res.velocities # example: access local velocity

tot_force = res.extract_force() # example: calculate total force
print(tot_force)