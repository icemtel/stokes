import mesh
import mesh.plot.trimesh_viewer as mplot


folder = 'data/cilia_plane'

num_phases  = 20
phase1, phase2, bp_phase = 0, 10, 16
phases = [phase1, phase2, *[bp_phase for _ in range(8)]]

#  mv = mplot.MeshViewer(tdir)
mv = mplot.FlagellaPlaneViewer(folder, phases=phases, num_phases=num_phases)

mv.show()