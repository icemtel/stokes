'''
Advanced example - create cilia and a plane with local refinement.
'''
from machemer import num_phases, flag_length, create_cilia_and_plane
import numpy as np
import FBEM, mesh

output_folder = 'data/cilia/'

# from hydro../try03b; only removed leading zero in integer parameters, and removed extra lines
mesh_params = {'longitude_grid': 60,
               'azimuth_grid': 8,
               'plane_width': 1.5,
               'max_plane_elem_area': 20.0,
               'plane_radius': 60,
               'flag_radius': 0.125  # cilia radius
               }

fbem_params = dict(tol=5e-4,
                   jpre=2,
                   ratio=1.15,
                   ngauss=7,
                   maxl=30,
                   nrmax=10)

x, y, z = 18, 0, 0.25 # micron; (x,y) - relative positions of cilia; z = elevation above the plane

positions = [(-x /2, - y/2, z), (x  /2 , y/2, z)] # 3D positions of cilia
rotations = [np.eye(3), np.eye(3)] # rotation matrices in 3D; for each cilium
phase_vector = [0, 10] # phases of two cilia - integer from 0 to num_phases - 1
phase_speed = [1, 0] # 0 if moves, 1 if does not move
                     # In our approach we only need 1 moving cilium to study interactions

# All complexity is hidden in the function below.
# It creates cilia on the given positions, with given rotations and in given phases of the beat
# mesh parameters for the plane and for the cilia is given by mesh_params
system = create_cilia_and_plane(positions, rotations,
                           phase_vector, phase_speed, refinement=None, **mesh_params)

# Get parameters of FBEM
fbem_params_full =  FBEM.config.default_values_dict.copy() # load default parameters
fbem_params_full.update(fbem_params) # update it with our parameters

# Run FBEM = solve Stokes eq; write output in the output folder
FBEM.run(system, output_folder, params=fbem_params_full)
