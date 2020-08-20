import myOS
import FBEM
import h5py
import FBEM.logs


def prepare_csv_line(*entries, delimeter=","):
    '''
    Prepare a list of objects for writing into a csv file.
    '''
    line_str_list = map(str, entries)
    line = delimeter.join(line_str_list) + "\n"
    return line



def get_ranges_csv_str(input_folder):
    '''
    Read from `ranges.csv` what range of nodes/triangles each geometrical object had.
    '''
    try:
        with open(myOS.Path(input_folder, 'ranges.csv'), 'r') as ranges_csv:
            ranges_csv_str = ranges_csv.read()
    except:
        ranges = FBEM.load_ranges(input_folder)
        object_names = list(ranges.coords.keys())
        header = prepare_csv_line('name', 'coords_start', 'coords_end', 'trias_start', 'trias_end')
        ranges_csv_str = header
        for name in object_names:
            coords_start, coords_end = ranges.coords[name]
            trias_start, trias_end = ranges.trias[name]
            row_vals = [name,coords_start,coords_end,trias_start, trias_end]
            ranges_csv_str +=  prepare_csv_line(*row_vals)

    return ranges_csv_str


def fbem_res_to_hdf5_handle(input_folder, output_file, group, metadata, float_type='f8', compression_level=9):
    '''
    :param group: folder-like name
    :param metadata: in the form of dictionary; This argument is compulsory in order to avoid mistakes
    :param float_type:
    :param compression_level: int from 0 to 9
    :return:
    '''
    # Read data with FBEM package
    group = myOS.Path(group).as_posix()
    fbem_data = FBEM.extract_all_data(input_folder)
    node_coords, trias = FBEM.read_all_triangulation_input(input_folder / 'input.dat')
    log_data = FBEM.logs.extract_data(input_folder)
    with open(input_folder / 'output.log', 'r') as logfile:  # Raw Log file
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
    if metadata is not None:
        g.attrs.update(metadata)
    # remembery/ranges - write columns separetely; otherwise pandas.DataFrame.to_hdf takes too much space
    ranges_csv_str = get_ranges_csv_str(input_folder)
    g.create_dataset('ranges', data=ranges_csv_str)



def subgroups_names(group, filename=None):
    '''
    :param group: h5py.Group unless filename is given
    :param filename: If given, open this file. group is treated as a group identifier.
    :return:
    '''
    if filename is not None:
        f = h5py.File(filename)
        group = myOS.Path(group).as_posix()
        g = f[group]
    else:
        g = group
    subgroups_list = []
    for key, obj in g.items():
        if isinstance(obj, h5py.Group):
            subgroups_list.append(key)
    if filename is not None:
        f.close()
    return subgroups_list


def visit_dirtree(folder_root, stuff_to_do, folder_relative='.'):
    folder = myOS.pathjoin(folder_root, folder_relative)
    for subdir in myOS.subdirs(folder):
        visit_dirtree(folder_root, stuff_to_do, myOS.Path(folder_relative, subdir))
    return stuff_to_do(folder_root, folder_relative)


def fbem_res_to_hdf5(input_folder, output_filename, group, metadata, mode='a', float_type='f8', compression_level=9):
    with h5py.File(output_filename, mode) as f:
        return fbem_res_to_hdf5_handle(input_folder, f, group, metadata, float_type, compression_level)



def fbem_res_tree_to_hdf5(input_folder, output_filename, mode='a', float_type='f8', compression_level=9, root_group='.'):
    '''
    Browse directory tree - try to exctract simulation result from every folder; If an error occurs - skip the folder.
    Exctract raw log files from the root.
    With mode 'a' will append to an existing file. But the existing groups will not be overwritten
    (dataset_create() will throw an error, which will be ignored and the program will continue)
    '''
    import h5py

    with h5py.File(output_filename, mode) as f:
        root_group = myOS.Path(root_group).as_posix()
        f = f[root_group]
        def write_simulation(folder_root, folder_relative):
            try:
                fbem_res_to_hdf5_handle(myOS.Path(folder_root, folder_relative), f, group=folder_relative,
                                        metadata={}, float_type=float_type, compression_level=compression_level)
                print("Sucess:", str(folder_relative))
            except:
                print("Skipped:", str(folder_relative))
                pass

        visit_dirtree(input_folder, write_simulation)
        try:
            with open(input_folder / 'finished.log', 'r') as logfile:
                log_str = logfile.read()
            f.create_dataset('finished.log', data=log_str)
            with open(input_folder / 'sim.log', 'r') as logfile:
                log_str = logfile.read()
            f.create_dataset('sim.log', data=log_str)
        except:
            pass
