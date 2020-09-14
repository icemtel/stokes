import FBEM
import h5py
import FBEM.logs
import json
from FBEM.various import path_to_string, subdirs
import os


def get_ranges_csv_str(input_folder):
    '''
    Read from `ranges.csv` what range of nodes/triangles each geometrical object had.
    '''
    with open(os.path.join(input_folder, 'ranges.csv'), 'r') as ranges_csv:
        ranges_csv_str = ranges_csv.read()
    return ranges_csv_str


def read_metadata(folder, filename='meta.json'):
    with open(os.path.join(folder, filename), 'r') as f:
        meta_dict = json.load(f)
    return meta_dict


def subgroups(group):
    '''
    :param group: h5py.Group
    :return: list of subgroup names (keys) and h5py group objects
    '''
    subgroups_list = []
    for key, obj in group.items():
        if isinstance(obj, h5py.Group):
            subgroups_list.append((key, obj))
    return subgroups_list

def subgroup_names(group):
    '''
    :param group: h5py.Group
    :return: list of subgroup names (keys)
    '''
    subgroups_list = []
    for key, obj in group.items():
        if isinstance(obj, h5py.Group):
            subgroups_list.append(str(key))
    return subgroups_list


def visit_dirtree(folder_root, stuff_to_do, folder_relative='.'):
    folder = os.path.join(folder_root, folder_relative)
    for subdir in subdirs(folder):
        visit_dirtree(folder_root, stuff_to_do, os.path.join(folder_relative, subdir))
    return stuff_to_do(folder_root, folder_relative)


def fbem_res_tree_to_hdf5(input_folder, output_filename, mode='a', float_type='f8', compression_level=9, root_group='.',
                          report_progress=True):
    '''
    Browse directory tree - try to extract FBEM results from every folder;
    - Folder is skipped if a error occurs (e.g. no FBEM results found in an intermediate folder)
    - Extract raw log files from the input folder.
    - Load metadata as hdf5 group attributes from meta.json
    :param mode: 'a' will append to an existing file. But the existing groups will not be overwritten
                     (dataset_create() will throw an error, which will be ignored and the program will continue)
    See what other parameters do in fbem_res_to_hdf5_handle
    '''
    with h5py.File(output_filename, mode) as f:
        root_group = path_to_string(root_group)
        f = f[root_group]

        def write_simulation(folder_root, folder_relative):
            try:
                fbem_res_to_hdf5_handle(os.path.join(folder_root, folder_relative), f, group=folder_relative,
                                        float_type=float_type, compression_level=compression_level)
                if report_progress is True:
                    print("Sucess:", str(folder_relative))
            except KeyboardInterrupt: # If there was a keyboard interrupt -> stop computation
                raise
            except: # Any other error => skip it and continue to the next folder
                if report_progress is True:
                    print("Skipped:", str(folder_relative))
                pass

        visit_dirtree(input_folder, write_simulation)
        try:
            with open(os.path.join(input_folder, 'finished.log'), 'r') as logfile:
                log_str = logfile.read()
            f.create_dataset('finished.log', data=log_str)
            with open(os.path.join(input_folder, 'sim.log'), 'r') as logfile:
                log_str = logfile.read()
            f.create_dataset('sim.log', data=log_str)
        except:
            pass

def fbem_res_to_hdf5(input_folder, output_filename, group, metadata_extra, mode='a', float_type='f8',
                     compression_level=9):
    with h5py.File(output_filename, mode) as f:
        return fbem_res_to_hdf5_handle(input_folder, f, group, metadata_extra, float_type, compression_level)


def fbem_res_to_hdf5_handle(input_folder, output_file, group, metadata_extra=None, float_type='f8',
                            compression_level=9):
    '''
    Save data from FBEM simulation folder to a group in hdf5 file.
    - metadata will be read from `meta.json`
    - additional metadata can be passed with `metadata_extra` parameter
    - metadata is saved as group attributes
    :param group: folder-like name
    :param metadata_extra: dictionary
    :param float_type: f8 = 64-bit floating-point number
    :param compression_level: int from 0 to 9
    '''
    # Read data with FBEM package
    group = path_to_string(group)
    fbem_data = FBEM.extract_all_data(input_folder)
    node_coords, trias = FBEM.read_all_triangulation_input(os.path.join(input_folder, 'input.dat'))
    log_data = FBEM.logs.extract_data(input_folder)
    with open(os.path.join(input_folder, 'output.log'), 'r') as logfile:  # Raw Log file
        log_str = logfile.read()

    compress_params = dict(compression='gzip', compression_opts=compression_level)  # from 0 to 9; in h5py default 4
    g = output_file.create_group(group)
    # output.dat
    g.create_dataset('coords', data=fbem_data.coordinates, dtype=float_type, **compress_params)
    g.create_dataset('forces', data=fbem_data.forces, dtype=float_type, **compress_params)
    g.create_dataset('velocities', data=fbem_data.velocities, dtype=float_type, **compress_params)
    g.create_dataset('visc', data=fbem_data.visc)
    # input.dat
    g.create_dataset('node_coords', data=node_coords, dtype=float_type, **compress_params)
    g.create_dataset('trias', data=trias, **compress_params)
    # output.log
    log_ds = g.create_dataset('log_raw', data=log_str)
    log_ds.attrs['bePRE'] = log_data.bePRE
    log_ds.attrs['beUNPRE'] = log_data.beUNPRE
    log_ds.attrs['time_cpu'] = log_data.time_cpu
    log_ds.attrs['info1'] = log_data.info1
    # info1 =  -4 if the algorithm failed to converge in maximum number of iterations; else 0
    log_ds.attrs['numIter'] = log_data.numIter
    # metadata
    try:
        metadata = read_metadata(input_folder)
        g.attrs.update(metadata)
    except:
        pass
    if metadata_extra is not None:
        g.attrs.update(metadata_extra)
    # Save ranges.csv as text; pandas.DataFrame.to_hdf takes too much space
    ranges_csv_str = get_ranges_csv_str(input_folder)
    g.create_dataset('ranges', data=ranges_csv_str)
