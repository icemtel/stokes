import mesh
import FBEM

radii = list(range(1, 5))


def run_simulation(folder, size):
    sphere = mesh.sphere_create('sphere', radius=size, velocity=(1, 0, 0), grid=3)
    FBEM.run(sphere, folder, cnd_path='input2018.cnd')


def run_sequential(radii):
    for radius in radii:
        folder = 'spheres/expected/radius_{0}'.format(radius)
        run_simulation(folder, radius)


run_sequential(radii)
