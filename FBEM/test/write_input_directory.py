import input_write
import mesh
import FBEM


system = mesh.sphere_create('sphere')


input_write.write_input(system, 'test_output')