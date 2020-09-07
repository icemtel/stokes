import numpy as np
import scipy.linalg as lin
import h5py
import pandas as pd
import os
from FBEM.various import path_to_string, Path


# Read input file
def read_tolerance(folder):
    '''
    read the 7nth thing from a line, replace D with E (e.g. in "0.1D-1"), transform to a float
    '''
    with open(os.path.join(folder, "input.cnd"), 'r') as file:
        line = file.readline()
        line_list = line.split()
        tol_str = line_list[6]
        tol_str_refined = tol_str.replace("D", "E")
        tol = float(tol_str_refined)
        return tol


def read_viscosity(folder, infile="input.dat"):
    '''
    Skip two lines, read the third thing from the line, transform to a float.
    '''
    with open(os.path.join(folder, infile), 'r') as file:
        file.readline()
        file.readline()
        line = file.readline()
        line_list = line.split()
        visc_str = line_list[2]  # read tolerance from the correct position
        return float(visc_str)


# Calculate physical quantities
def calc_flowfield(coordinates, forces, visc=1):
    coordinates = np.array(coordinates)
    const = 1 / 8 / np.pi / visc

    def hfunc(r):
        dr = r - coordinates
        ndr = np.linalg.norm(dr, axis=1)
        fdr = np.array(np.sum(forces * dr, axis=1))
        return np.sum(np.transpose((np.transpose(np.transpose(dr) * fdr / (ndr * ndr)) + forces)) * const / ndr, axis=1)

    return hfunc


# Read output file
class ResultsData:
    def __init__(self, forces, velocities, coordinates, visc, areas=None):
        self.forces = forces  # - Hydrodynamic friction forces (not the force density!) with negative sign.
        # (forces equal to the ones which would compensate fluid friction)
        self.velocities = velocities
        self.coordinates = coordinates
        self.visc = visc  # viscosity
        self.areas = areas  # element areas; were only needed to calculate forces, but it doesn't hurt to keep it anyway

    def extract_force(self):
        return np.sum(self.forces, axis=0)

    def extract_center(self):
        return np.mean(self.coordinates, axis=0)

    def extract_torque(self, origin=None):
        if origin is None:
            origin = self.extract_center()
        return np.sum(np.cross(self.coordinates - origin, self.forces), axis=0)

    def extract_flowfield(self):
        return calc_flowfield(self.coordinates, self.forces, self.visc)


# Use it if needed to read mesh from input file
def read_all_triangulation_input(filename):
    """
    read points and triangulation and return it.
    Points numbers in triangulation start from 0.
    """
    f = open(filename, 'r')
    points = []
    trias = []
    pointFlag = False
    triaFlag = False
    for line in f:
        if pointFlag:
            try:
                pos_line = line.split()[1:]
                points.append([float(h) for h in pos_line])
            except:
                pointFlag = False
                triaFlag = True
        elif triaFlag:
            tria_line = line.split()[1:4]
            trias.append([int(val) - 1 for val in tria_line])
        elif '$ Nodes' in line:
            pointFlag = True
    f.close()
    return np.array(points), np.array(trias, dtype=np.int)  # points,trias


def read_triangulation_by_names_input(object_names, folder, input_name='input.dat'):
    '''
    :return: list of coords, list of trias, corresponding to each of the input objects
    TODO: should work faster if don't iterate over the names of objects which have their data already loaded
    TODO: And load all points of object after encountering the first one?
    '''
    ranges = load_ranges(folder)
    inputfile = os.path.join(folder, input_name)

    result = {}
    for name in object_names:
        posiRange, triaRange = ranges.coords[name], ranges.trias[name]
        posi = np.zeros((posiRange[1] - posiRange[0] + 1, 3))
        tria = np.zeros((triaRange[1] - triaRange[0] + 1, 3), dtype=np.int)
        result[name] = posi, tria  # points, trias

    triaFlag = False
    posiFlag = False
    with open(inputfile, 'r') as f:  # in GK was just f = open(..) without closing
        for line in f:
            if '$ Nodes (Nod' in line:
                posiFlag = True
            if '$ Elements and Boundary Co' in line:
                triaFlag = True
                posiFlag = False
            if posiFlag:
                try:
                    (a, b, c, d) = line.split()
                except:
                    continue
                for name in object_names:
                    posiRange, triaRange = ranges.coords[name], ranges.trias[name]

                    if int(a) > posiRange[0] and int(a) <= posiRange[1] + 1:
                        result[name][0][int(a) - 1 - posiRange[0]] = (float(b), float(c), float(d))
                        break

            if triaFlag:
                try:
                    (a, b, c, d, e, f, g, h, i, j) = line.split()
                except:
                    continue
                for name in object_names:
                    posiRange, triaRange = ranges.coords[name], ranges.trias[name]
                    if int(a) > triaRange[0] and int(a) <= triaRange[1] + 1:
                        result[name][1][int(a) - 1 - triaRange[0]] = (int(b) - 1 - posiRange[0],
                                                                      int(c) - 1 - posiRange[0],
                                                                      int(d) - 1 - posiRange[0])
                        break
    # Return a coords and trias lists for consistency with other functions
    coords_list = [result[name][0] for name in object_names]
    trias_list = [result[name][1] for name in object_names]
    return coords_list, trias_list


# Returns np.array!
def read_triangulation_input(filename, posiRange, triaRange):
    """
    filename is the name of the input file. (usually 'input.dat')
    posiRange: indices of coordinates.
    triaRange: indices of triangulation.
    return two numpy arrays, containing the coordinates and the triangulation
    with respect to those coordinates.
    """

    tria = np.zeros((triaRange[1] - triaRange[0] + 1, 3), dtype=np.int)
    posi = np.zeros((posiRange[1] - posiRange[0] + 1, 3))
    triaFlag = False
    posiFlag = False
    with open(filename, 'r') as f:  # in GK was just f = open(..) without closing
        for line in f:
            if '$ Nodes (Nod' in line:
                posiFlag = True
            if '$ Elements and Boundary Co' in line:
                triaFlag = True
                posiFlag = False
            if posiFlag:
                try:
                    (a, b, c, d) = line.split()
                except:
                    continue
                if int(a) > posiRange[0] and int(a) <= posiRange[1] + 1:
                    posi[int(a) - 1 - posiRange[0]] = (float(b), float(c), float(d))

            if triaFlag:
                try:
                    (a, b, c, d, e, f, g, h, i, j) = line.split()
                except:
                    continue
                if int(a) > triaRange[0] and int(a) <= triaRange[1] + 1:
                    tria[int(a) - 1 - triaRange[0]] = (int(b) - 1 - posiRange[0],
                                                       int(c) - 1 - posiRange[0],
                                                       int(d) - 1 - posiRange[0])

    return (posi, tria)


def read_triangulation_by_name_input(object_name, folder, input_name='input.dat'):
    ranges = load_ranges(folder)
    posiRange, triaRange = ranges.coords[object_name], ranges.trias[object_name]

    inputfile = os.path.join(folder, input_name)
    posi, tria = read_triangulation_input(inputfile, posiRange, triaRange)
    return (posi, tria)


def triangleArea(v1, v2, v3):
    """
    given three position vectors, calculate the area of a triangle, using
    Heron's formula.
    """
    [v1, v2, v3] = [np.array(v) for v in [v1, v2, v3]]
    [a, b, c] = [lin.norm(d) for d in [v1 - v2, v2 - v3, v3 - v1]]
    s = (a + b + c) / 2.0
    A = np.sqrt(s * (s - a) * (s - b) * (s - c))
    return A


# Returns dictionary!
# def triangleAreas(filename, posiRange, triaRange):
#     """
#     filename is the input filename.
#     """
#     (posi, tria) = triangulation(filename, posiRange, triaRange)
#     areas = {}
#     for t in tria.keys():
#         areas[t] = triangleArea(posi[tria[t][0]], posi[tria[t][1]], posi[tria[t][2]])
#     return areas

#  Returns scipy array!
def read_triangle_areas_input(filename, posiRange, triaRange):
    """
    filename is the path to 'input.dat'
    """
    (posi, tria) = read_triangulation_input(filename, posiRange, triaRange)
    areas = np.zeros((triaRange[1] - triaRange[0] + 1))
    for (i, t) in enumerate(tria):
        areas[i] = triangleArea(posi[t[0]], posi[t[1]], posi[t[2]])
    return areas


def _exctract_data(posiRange, triaRange,
                   infile='input.dat',
                   outfile='output.dat'):
    """
    given a number range, that correspond to an object,
    read velocities, forces and positions and areas as np.arrays.
    """
    areas = read_triangle_areas_input(infile, posiRange, triaRange)

    num = triaRange[1] - triaRange[0] + 1
    velocities = np.zeros((num, 3))
    forces = np.zeros((num, 3))
    positions = np.zeros((num, 3))

    with open(outfile, 'r') as file:
        for line in file:
            try:
                (a, b, c, d, e, f, g, h, i, j) = line.split()
                index = int(a)
                if index > triaRange[0] and index <= triaRange[1] + 1:
                    velocities[index - triaRange[0] - 1] = (float(b), float(c), float(d))
                    forces[index - triaRange[0] - 1] = (float(e), float(f), float(g))
                    positions[index - triaRange[0] - 1] = (float(h), float(i), float(j))
                if index > triaRange[1]:
                    break
            except:
                continue

    for k in range(num):  # Force density -> forces
        forces[k] *= areas[k]

    visc = read_viscosity('.', infile)

    return ResultsData(forces, velocities, positions, visc, areas)


class Ranges:
    '''
    Class contains range of coordinates and triangles, which belong to each meshed object.
    '''

    def __init__(self):
        # Will be filled with dictionaries
        self.names = []  # list of objects
        self.coords = {}
        self.trias = {}

    def get_names(self):
        '''
        :return: object names without "all"
        '''
        names = self.names.copy()
        names.remove("all")
        return names

def load_ranges(folder):
    '''
    Create Ranges class from a ranges.csv file.
    '''
    ranges = Ranges()
    objects_df = pd.read_csv(os.path.join(folder, 'ranges.csv'))
    for idx, row in objects_df.iterrows():
        name, coords_start, coords_end, trias_start, trias_end = row
        ranges.names.append(name)
        ranges.coords[name] = (coords_start, coords_end)
        ranges.trias[name] = (trias_start, trias_end)
    return ranges


def extract_data_by_name(object_name,
                         folder='.',
                         infile='input.dat',
                         outfile='output.dat'):
    ranges = load_ranges(folder)

    res = _exctract_data(ranges.coords[object_name],
                         ranges.trias[object_name],
                         infile=os.path.join(folder, infile),
                         outfile=os.path.join(folder, outfile))
    return res


def extract_data_by_names(object_name_list,  # TODO: enter file only once!
                          folder='.',
                          infile='input.dat',
                          outfile='output.dat'):
    '''
    Returns list of ResultsData, corresponding to each object in obejct_name_list
    '''
    ranges = load_ranges(folder)
    res_list = []
    for object_name in object_name_list:
        res = _exctract_data(ranges.coords[object_name],
                             ranges.trias[object_name],
                             infile=os.path.join(folder, infile),
                             outfile=os.path.join(folder, outfile))
        res_list.append(res)
    return res_list


def extract_all_data(folder='.', infile='input.dat', outfile='output.dat'):
    return extract_data_by_name('all',
                                folder=folder,
                                infile=infile,
                                outfile=outfile)


# hdf5

def read_viscosity_hdf5(file_handle, group='.'):
    return file_handle[group]['visc'][()]


def get_df_from_csv_str(csv_str):
    '''
    Convert str object to df. Assuming that str object has a structure of csv file.
    '''
    import io
    csv_file = io.StringIO(csv_str)
    df = pd.read_csv(csv_file)
    return df


def load_ranges_hdf5(file_handle, group='.'):
    '''
    Helper function to load ranges/remembery in one line
    '''
    g = file_handle[path_to_string(group)]
    ranges_csv_str = g['ranges'][()]
    ranges = Ranges()
    objects_df = get_df_from_csv_str(ranges_csv_str)
    for idx, row in objects_df.iterrows():
        name, coords_start, coords_end, trias_start, trias_end = row
        ranges.names.append(name)
        ranges.coords[name] = (coords_start, coords_end)
        ranges.trias[name] = (trias_start, trias_end)
    return ranges


def _extract_data_hdf5(triaRange, file_handle, group='.'):
    """
    - given a number range, that correspond to an object,
    read velocities, forces and positions and areas as np.arrays.
    - load from hdf5 file.
    """
    g = file_handle[path_to_string(group)]
    t0, t1 = triaRange
    forces = g['forces'][t0:t1 + 1]
    velocities = g['velocities'][t0:t1 + 1]
    positions = g['coords'][t0:t1 + 1]
    visc = read_viscosity_hdf5(g)

    # Calculate areas
    node_positions = g['node_coords'][:]
    trias = g['trias'][t0:t1 + 1]
    areas = np.array([triangleArea(node_positions[t[0]], node_positions[t[1]], node_positions[t[2]]) for t in trias])

    return ResultsData(forces, velocities, positions, visc, areas)


def extract_all_data_hdf5(file, group='.'):
    g = file[path_to_string(group)]

    forces = g['forces'][:]
    velocities = g['velocities'][:]
    positions = g['coords'][:]
    visc = read_viscosity_hdf5(g)
    # Calculate areas
    node_positions = g['node_coords'][:]
    trias = g['trias'][:]
    areas = np.array([triangleArea(node_positions[t[0]], node_positions[t[1]], node_positions[t[2]])
                      for t in trias])
    return ResultsData(forces, velocities, positions, visc, areas)


def extract_data_by_name_hdf5(name, file_handle, group='.'):
    ranges = load_ranges_hdf5(file_handle, group)

    res = _extract_data_hdf5(ranges.trias[name],
                             file_handle, group)
    return res


def extract_data_by_names_hdf5(names, file, group='.'):
    '''
    Returns list of ResultsData, corresponding to each object in obejct_name_list
    '''
    ranges = load_ranges_hdf5(file, group)

    g = file[path_to_string(group)]

    forces_full = g['forces'][()]
    velocities_full = g['velocities'][()]
    positions_full = g['coords'][()]
    node_positions = g['node_coords'][:]

    visc = read_viscosity_hdf5(g)

    res_list = []
    for name in names:
        t0, t1 = ranges.trias[name]
        forces = forces_full[t0:t1 + 1]
        velocities = velocities_full[t0:t1 + 1]
        positions = positions_full[t0:t1 + 1]
        # Calculate areas
        trias = g['trias'][t0:t1 + 1]
        areas = np.array([triangleArea(node_positions[t[0]], node_positions[t[1]], node_positions[t[2]])
                          for t in trias])
        # Save
        res = ResultsData(forces, velocities, positions, visc, areas)
        res_list.append(res)
    return res_list


def read_triangulation_hdf5(file, posiRange, triaRange, group='.'):
    g = file[group]

    coords = g['node_coords'][posiRange[0]:posiRange[1] + 1]
    trias = g['trias'][triaRange[0]:triaRange[1] + 1]
    return coords, trias


def read_triangulation_by_names_hdf5(names, file, group='.'):
    ranges = load_ranges_hdf5(file, group)
    coords_list = []
    trias_list = []
    for name in names:
        coords, trias = read_triangulation_hdf5(file, ranges.coords[name], ranges.trias[name], group)
        coords_list.append(coords)
        trias_list.append(trias)
    return coords_list, trias_list


def read_triangulation_by_name_hdf5(name, file, group='.'):
    coords_list, trias_list = read_triangulation_by_names_hdf5([name], file, group)
    return coords_list[0], trias_list[0]


def read_all_triangulation_hdf5(file, group='.'):
    g = file[group]
    coords = g['node_coords'][()]
    trias = g['trias'][()]
    return coords, trias


class Source:
    '''
    One class to handle both hdf5 and text file input
    '''

    def __init__(self, path, group='.'):
        '''
        :param path: either folder or hdf5 filename
        :param group: group in hdf5 file; ignored if `path` is a folder
        '''
        self.path = Path(path)
        self.group = group
        if not self.path.exists():
            raise ValueError("Path doesn't point to a hdf5 file or directory")

        if self.path.is_dir():
            self.is_hdf5 = False
        elif self.path.suffix in ['.h5', '.hdf5']:
            self.is_hdf5 = True
        else:
            raise NotImplementedError

    def read_triangulation(self, name='all'):
        if self.is_hdf5:
            with h5py.File(self.path, 'r') as file:
                return read_triangulation_by_name_hdf5(name, file, self.group)
        else:
            return read_triangulation_by_name_input(name, self.path)

    def read_triangulation_list(self, names):
        '''
        :return: Tuple: list of coords and list of triangles
        '''
        if self.is_hdf5:
            with h5py.File(self.path, 'r') as file:
                return read_triangulation_by_names_hdf5(names, file, self.group)
        else:
            return read_triangulation_by_names_input(names, self.path)

    def read_data(self, name='all'):
        if self.is_hdf5:
            with h5py.File(self.path, 'r') as file:
                return extract_data_by_name_hdf5(name, file, self.group)
        else:
            return extract_data_by_name(name, self.path)

    def read_data_list(self, names):
        '''
        :return: List of ResultsData objects, corresponding to each object name
        '''
        if self.is_hdf5:
            with h5py.File(self.path, 'r') as file:
                return extract_data_by_names_hdf5(names, file, self.group)
        else:
            return extract_data_by_names(names, self.path)

    def read_ranges(self):
        if self.is_hdf5:
            with h5py.File(self.path, 'r') as file:
                return load_ranges_hdf5(file, self.group)
        else:
            return load_ranges(self.path)
