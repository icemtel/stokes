import vedo

verts = [(50,50,50), (70,40,50), (50,40,80), (80,70,50)]
faces = [(0,1,2), (2,1,3), (1,0,3)]
# (the first triangle face is formed by vertex 0, 1 and 2)

# Build the polygonal Mesh object:
mesh = vedo.Mesh([verts, faces])
mesh.backColor('violet').lineColor('tomato').lineWidth(2)
labs = mesh.labels('id')


plotter = vedo.show(mesh, labs, __doc__, viewup='z', axes=1)
plotter.close()