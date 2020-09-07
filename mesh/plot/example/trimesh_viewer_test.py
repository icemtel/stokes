import mesh.plot.trimesh_viewer as plot3D

path = 'data/sphere_wall'

# Plot with random colors for each object
m = plot3D.MeshViewer(path, group='.')
m.show()

# Plot with pre-defined colors
names = ['sphere', 'plane']
colors = [(0., 1., 1., 1), (1., 1., 0, 1)]

m = plot3D.MeshViewer(path, group='.', names=names, colors=colors)
m.show()

# Plot all objects with the same (random) color
m = plot3D.MeshViewer(path, group='.', names=['all'], colors=None)
m.show()
