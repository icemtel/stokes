import mesh.plot.vedo_viewer as plot3D

path = 'data/sphere_wall'

# Plot with random colors for each object
m = plot3D.MeshViewer(path, group='.')
plotter = m.show(axes=1)
plotter.close()  # important to close plotter afterwards!

# Plot with pre-defined colors
names = ['sphere', 'plane']
colors = [None, 'grey'] # None to be replaced with a random color

m = plot3D.MeshViewer(path, group='.', names=names, colors=colors)
plotter = m.show(axes=2)
plotter.close()  # important to close plotter afterwards!

# Plot all objects with the same color
m = plot3D.MeshViewer(path, group='.', names=['all'], colors=None)
plotter = m.show(axes=3)
plotter.close()  # important to close plotter afterwards!
