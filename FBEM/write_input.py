import os
from datetime import datetime
import mesh.convert
import FBEM.config as cfg
from mesh import triangulate_system
from FBEM.various import prepare_csv_line





def write_input_to_file(filename, tria_generator, *tria_generator_args, description='',
                        external_flow_field=None):
    """
    Function, equivavelnt to Gary's write_input, except that now you can choose a destination file for input data
    :return: Triangulation object
    """
    triangulation = triangulate_system(*tria_generator_args, tria_generator=tria_generator,
                                       external_flow_field=external_flow_field)
    triangulation2file(filename=filename, triangulation=triangulation, description=description)
    return triangulation


def write_inputDat_to_folder(folder, system, external_flow_field=None):
    '''
    This function basically calls one function from Gary's code, assuming tria_generator = fuse_mesh.
    :return: Triangulation object
    '''
    input_path = os.path.join(folder, 'input.dat')
    triangulation = write_input_to_file(input_path, mesh.fuse_mesh, system, external_flow_field=external_flow_field)
    return triangulation


def write_ranges(filename, mesh):
    """
    mesh contains the information about ranges of coordinates and the
    triangulation of a mesh (coordRanges, triaRanges).
    """
    with open(filename, 'w') as f:
        header = prepare_csv_line("name", "coords_start", "coords_end", "trias_start", "trias_end")
        f.write(header)
        for name in mesh.coordRanges:
            coords_start, coords_end = mesh.coordRanges[name]
            trias_start, trias_end = mesh.triaRanges[name]
            line = prepare_csv_line(name, coords_start, coords_end, trias_start, trias_end)
            f.write(line)


def write_input_and_ranges(folder, system, external_flow_field=None):
    '''
    Not tested with external flow field!
    Used to write remembery.py, now it's ranges.csv
    '''
    from mesh import prepare_system
    system = prepare_system(system)
    meshGK = write_inputDat_to_folder(folder, system, external_flow_field)

    remembery_path = os.path.join(folder, 'ranges.csv')
    write_ranges(remembery_path, meshGK)


def write_input_cnd(folder, params=None, name='input.cnd'):
    '''
    :param folder: Folder to write the input.cnd file;
    :param params: dictionary with .cnd parameters; Missing one are replaced by the default ones
    :return:
    '''
    params_dict = dict(cfg.default_values_dict)  # make a copy
    if params is not None:
        params_dict.update(params)  # Replace the default values with the given ones
    with open(os.path.join(folder, name), 'w') as cnd:
        # Write the first line
        for key in ['eps', 'maxl', 'kmp', 'jscal', 'jpre', 'nrmax', 'tol']:
            val = params_dict[key]
            if val == int(val):  # To avoid writing long integers as a floating number
                cnd.write(str(val) + '\t')
            else:
                cnd.write('{:0.15G}\t'.format(val))
        cnd.write('! eps, maxl, kmp, jscal, jpre, nrmax, tol')
        cnd.write('\n')
        for key in ['maxdep', 'mindep', 'maxepc', 'maxcel', 'nterm', 'ngauss', 'ratio']:
            val = params_dict[key]
            if val == int(val):
                cnd.write(str(val) + '\t')
            else:
                cnd.write('{:0.15G}\t'.format(val))
        cnd.write("! maxdep, mindep, maxepc, maxcel, nterm, ngauss, ratio")


def triangulation2file(filename='input.dat',
                       triangulation=None,
                       description=''):
    """
    Originally - by GK.
    :param triangulation: Triangulation object from `mesh.Triangulation`
    """
    with open(filename, 'w') as f:
        if description != '':
            description += ',\t'

        now = datetime.now()
        f.write(description + now.strftime("%A %d. %B %Y, %H:%M:%S") + '\n')
        f.write('\t1       ! Problem Type (Do not change this number)\n')

        numTria = len(triangulation.triangulation)
        numCoor = len(triangulation.coordinates)
        f.write('\t{0}\t{1}\t{2}\t ! No. of Elements, Nodes, Mu (Viscosity)\n'.format(numTria, numCoor, 1))
        f.write(' $ Nodes (Node #, x, y, and z coordinates):\n')

        for i in range(numCoor):  # Write coords
            f.write('{0}\t{1[0]}\t{1[1]}\t{1[2]}\n'.format(i + 1, triangulation.coordinates[i]))
        f.write(
            ' $ Elements and Boundary Conditions (Elem #, Connectivity, BC Type (1=velocity given/2=traction given, in x,y,z) and given BC Values (in x,y,z)):\n')
        for i in range(numTria):  # Write elements +BCo
            jj = triangulation.triangulation[i]
            ii = (int(jj[0]) + 1, int(jj[1]) + 1, int(jj[2]) + 1)
            v1 = triangulation.velocities[int(jj[0])]
            v2 = triangulation.velocities[int(jj[1])]
            v3 = triangulation.velocities[int(jj[2])]
            v = (v1 + v2 + v3) / 3
            f.write('{0}\t{1[0]:d}\t{1[1]:d}\t{1[2]:d}\t'.format(i + 1, ii))
            f.write('1\t1\t1\t{0[0]}\t{0[1]}\t{0[2]}\n'.format(v))


if __name__ == '__main__':
    params = dict(eps=0.14000000616, tol=10 ** -15, )
    write_input_cnd('', params)