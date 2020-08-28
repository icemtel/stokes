import matplotlib.pyplot as plt
from plot3D.mplMeshViewer import MeshViewer


mv = MeshViewer('data/sphere_wall')
mv.create_ax()
mv.triangular_mesh()
mv.show()