'''
We can visualize 3D mesh with one of the supported packages.

Best: vedo or trimesh
'''
import mesh.plot.vedo_viewer as mplot

folder = 'data/sphere_presaved/'

m = mplot.MeshViewer(folder)
plotter = m.show()
plotter.close()

