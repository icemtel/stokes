'''
force density:
OK: `all`
OK: 1 object; 1 object in array
OK: 2 objects
OK: 2 commands with different objects

OK: indices to skip don't work?
'''
from mesh.plot.mlab_viewer import MeshViewer

folder = 'data/cilia_plane2'  # 'data/sphere_wall'
cilium_radius = 0.11

plotter = MeshViewer(folder)

plotter.triangular_mesh(['flagellum_1', 'flagellum_2'], representation='fancymesh')
# plotter.force_density_arrows(['flagellum_2'],n=12, indices_to_skip=list(range(-12,0)))
plotter.force_density_arrows(['flagellum_1', 'flagellum_2'], points_per_arrow=12, indices_to_skip=list(range(-12, 0)),
                             offset_distance=cilium_radius, inverse_direction=True)
plotter.velocity_arrows(['flagellum_1', 'flagellum_2'], points_per_arrow=12, indices_to_skip=list(range(-12, 0)), )

plotter.show()

### Test averaging
# import scipy as sp
# data = plotter.source.read_data('flagellum_1')
#
# forces = data.forces
# areas = data.areas
#
# print("avg force", sp.average(forces, axis=0))
#
# avg_forces = mmv._average_values(forces / areas[:, sp.newaxis], areas)
# print(avg_forces.shape)
# print(avg_forces[:3])
# print("avg force 2", sp.average(avg_forces * areas[:, sp.newaxis], axis=0))
#
#
# avg_forces = mmv._average_values(forces / areas[:, sp.newaxis], areas, n=5)
# print(avg_forces.shape)
# print(avg_forces[:3])
# print("avg force 2", sp.average(avg_forces * areas[:, sp.newaxis], axis=0))
