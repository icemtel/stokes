import numpy as np
import mesh
import mesh.plot.trimesh_viewer as mplot # visualize

# Generate some data
length = 10 # length of flagellum, um
radius = 0.125 # flagellum radius
long_grid = 30 # longitudal grid
azimuth_grid = 8


xs = np.linspace(-1, 1, long_grid)
ys = xs ** 2
zs = np.zeros_like(xs)



points = np.array([xs, ys,zs]).T
# Generate tangents
# dy/dx = x
tangent_func = lambda x: np.array([1, x, 0]) / np.linalg.norm(np.array([1, x, 0]))
tangents = np.array([tangent_func(x) for x in xs])
# Why do we need tangents and normals?
# there is more than 1 way to create mesh for a line objec - normals define whether the mesh gets twisted
normal_func = lambda x: np.array([-x, 1, 0]) / np.linalg.norm(np.array([-x, 1, 0]))
normals = np.array([normal_func(x) for x in xs])
# Generate velocity
beat_freq = 2 * np.pi * 32 # 2pi / 31.25 ms beat frequency
# drrdphi = load_drrdphi(phase, longitude_grid=longitude_grid)
# velocities = phase_speed * drrdphi * beat_freq
velocities = np.zeros_like(points) # for a test - zero velocity

idx = 0 # index of cilium
name = 'flagellum_' + str(idx + 1)
flagellum = mesh.flagellum_vel_create(name=name,
                                      points=points,
                                      velocities=velocities,
                                      tangents=tangents,
                                      normals=normals,
                                      radius=radius,
                                      azimuth_grid=azimuth_grid,
                                      translation=np.zeros(3),
                                      rotation=np.eye(3))


#plane = mesh.prepare_system(plane) - sometimes needed
tri = mesh.triangulate_system(flagellum) # Triangulation class

m = mplot.triangulation_to_trimesh(tri) # class of TriMesh, suitable for plotting

m.show() # visualize - 3D