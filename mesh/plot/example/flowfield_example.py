import mesh.plot.flowfield as ff
import matplotlib.pyplot as plt
import matplotlib as mpl

folder = 'data/cilia_plane2'


flowfield = ff.extract_flowfield(folder)
projection = 'yz'
x1range = -15, 15
x2range = -1, 10
grid_color = 30
grid_arrows = 10
offset = 0


# Normalize
velocity_max = 0.1  # vectors_max[0]
norm = mpl.colors.Normalize(0, velocity_max)
# Plot
im = ff.plot_flowfield_color(flowfield, projection, x1range, x2range, offset,
                         grid=grid_color, interpolation='bilinear',
                         norm=norm, colorbar=False)
ff.plot_flowfield_arrows(flowfield, projection, x1range, x2range, offset,
                         grid=grid_arrows, zorder=3)
plt.colorbar(im)
plt.show()