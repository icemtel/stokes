'''
- Generate plot for the README.md file

Cilia phases used: 16, 3
'''
import mesh.plot.vedo_viewer as mplot
import numpy as np


folder = 'data/cilia/' # pre-saved results of step01

phases = [16, 3]
num_phases = 20
mv = mplot.FlagellaPlaneViewer(folder, phases=phases, num_phases=num_phases)
# plotter = mv.show()
# plotter.close()

# Plot force and velociy arrows
names = ['flagellum_1', 'flagellum_2']
scale = 2
min_arrow_length = 0.1 # um

# Velocity arrows
velocities = mplot.VelocityArrows(folder, names, points_per_arrow=32, scale=scale, min_arrow_length=min_arrow_length)
# Forces arrows
scale = - 0.5 # flip sign -> so that does not overlap with velocities
min_arrow_length = 0.1
forces = mplot.ForceArrows(folder, names, points_per_arrow=32, scale=scale, min_arrow_length=min_arrow_length)

assembly = mv + velocities + forces


# Camera location
scale = 2
z = 14
r = 30
psi = np.pi / 6 # polar angle
camera = dict(pos=scale *  np.array([-r * np.cos(psi), r * np.sin(psi), z]), viewup=[0,0,1], focalPoint=[0,-2 ,0.5])
size = 128 * np.array([4,3]) # window size
offscreen = False # Hide
interactive= True # should be false to execute the whole script
plotter = assembly.show(camera=camera, pos=(100,0), interactive=interactive,
                               size=size, offscreen=offscreen)
plotter.close()
