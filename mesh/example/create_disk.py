import mesh
import mesh.plot.trimesh_viewer as mplot # visualize



plane_radius = 10
plane_width = 1
max_elem_area = 1 # maximum area of a triangle on the face of the plane

refinement = None # advanced
refine_bot = False # whether to refine both top and bot surfaces or only the top one


plane = mesh.disk_create('plane', plane_radius, plane_width, max_area=max_elem_area,
                         extra_side_node_layers='auto',
                         refinement=refinement, refine_bot=refine_bot)

#plane = mesh.prepare_system(plane) - sometimes needed
tri = mesh.triangulate_system(plane) # Triangulation class

m = mplot.triangulation_to_trimesh(tri) # class of TriMesh, suitable for plotting

m.show() # visualize - 3D