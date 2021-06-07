'''
- disk - creates ellipsis; implemented better refinement
'''
import mesh
import mesh.plot.trimesh_viewer as mplot # visualize



name = 'plane'
sizes = (10, 5, 1)
grids = (10, 10, 1)

plane = mesh.cuboidXY_create(name, sizes, grids)
tri = mesh.triangulate_system(plane)

## Visualize
import mesh.plot.trimesh_viewer as mplot # visualize

m = mplot.triangulation_to_trimesh(tri) # class of TriMesh, suitable for plotting
m.show() # visualize - 3D