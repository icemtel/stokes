import mesh
import mesh.plot.vedo_viewer as mplot

folder = 'data/two_cilia_machemer0/' # cilia_plane'

mv = mplot.MeshViewer(folder)
# plotter = mv.show()
# plotter.close()

# Plot with arrows
names = ['flagellum_1', 'flagellum_2']
scale = 1
min_arrow_length = 0  # 1 um
arrows = mplot.VelocityArrows(folder, names, points_per_arrow=6, scale=scale, min_arrow_length=min_arrow_length)

assembly = mv + arrows
plotter = assembly.show()
plotter.close()
