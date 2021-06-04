'''
Plot geometry & output forces (exerted by cilia on the fluid) & velocities.

Visualizing forces and velocities is tricky:
We want to average over several nearby points, otherwise we have too many arrows
Right now, I just average over one-dimensional indices -> works for cilia.
Applying this code to other geometries may break the averaging
'''
import mesh.plot.vedo_viewer as mplot

folder = 'data/cilia_presaved/' # pre-saved results of step01

phases = [0, 5]
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

assembly = mv + velocities  + forces
plotter = assembly.show()
plotter.close()
