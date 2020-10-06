import matplotlib.pyplot as plt
from mesh.plot.mpl_viewer import MeshViewer

mv = MeshViewer('data/sphere_wall')
mv.create_ax()
mv.triangular_mesh()
mv.show()
