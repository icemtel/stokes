'''
Extract data: velocities, forces, etc.
[Folder sphere_presaved contains output expected after step00 in case the user is not able to run step00]
'''
import FBEM

folder = 'data/sphere_presaved/'

res = FBEM.extract_all_data(folder) # output  ResultsData class

coords = res.coordinates
velocities = res.velocities # example: access surface velocity
tot_force = res.extract_force() # example: calculate total force
print(tot_force)