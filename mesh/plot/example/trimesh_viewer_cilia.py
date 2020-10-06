import mesh
import mesh.plot.trimesh_viewer as mplot


folder = 'data/cilia_plane2'

num_phases  = 20
phases = [0, 5]

#  mv = mplot.MeshViewer(tdir)
mv = mplot.FlagellaPlaneViewer(folder, phases=phases, num_phases=num_phases)

mv.show()