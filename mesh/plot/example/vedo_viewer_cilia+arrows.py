'''
- In this example only the flagellum #1 moves
- Forces on the 2nd one are visibly only if the force scale is increased to `50`
'''

import mesh
import mesh.plot.vedo_viewer as mplot

folder = 'data/cilia_plane2/' # cilia_plane'

#mv = mplot.MeshViewer(folder) # simple way to display geometry
phases = [0, 5]
num_phases = 20
mv = mplot.FlagellaPlaneViewer(folder, phases=phases, num_phases=num_phases)
# plotter = mv.show()
# plotter.close()

# Plot with arrows
names = ['flagellum_1', 'flagellum_2']
scale = 2
min_arrow_length = 0.1 # um

# Velocity arrows
velocities = mplot.VelocityArrows(folder, names, points_per_arrow=32, scale=scale, min_arrow_length=min_arrow_length)
# Forces arrows
scale = - 0.5 # flip sign -> so that does not overlap with velocities
min_arrow_length = 0.1
forces = mplot.ForceArrows(folder, names, points_per_arrow=32, scale=scale, min_arrow_length=min_arrow_length)

assembly = mv + velocities  + forces
plotter = assembly.show()
plotter.close()
