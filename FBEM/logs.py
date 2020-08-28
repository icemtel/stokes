import pandas as pd
import os
from FBEM.various import path_to_string, subdirs, Path

class LogData:
    def __init__(self, info1, numIter, bePRE, beUNPRE, time_cpu, time_wall):
        self.info1 = info1  # info1 =  -4 if the algorithm failed in converge in maximum number of iterations; else 0
        self.numIter = numIter
        self.bePRE = bePRE
        self.beUNPRE = beUNPRE
        self.time_cpu = time_cpu
        self.time_wall = time_wall # wall-clock time spent to run the problem
        # TODO: wall-clock time is negative sometimes?! - don't use it or figure out what's the problem

    def __str__(self):
        return "info1 = {0},\tnumIter = {1},\tbePRE = {2:.3g},\tbeUNPRE = {3:.3g}," \
               "\ttime_cpu = {4:.3g},\ttime_wall={5:.3g}". \
            format(self.info1, self.numIter, self.bePRE, self.beUNPRE, self.time_cpu, self.time_wall)


def _extract_data(file, dtype):
    '''
    :param file: file object
    '''
    info_is_read = False
    be_read = False
    for line in file:
        if line[:8] == ' info(1)':
            linesplit = line.split()
            info1 = int(linesplit[2])
            numIter = int(linesplit[-1])  # Number of iterations
            info_is_read = True
        if info_is_read and line[:9] == ' rinfo(1)':
            linesplit = line.split()
            bePRE = float(linesplit[2])  # b.e. preconditioned
            beUNPRE = float(linesplit[-1])  # and unpreconditioned
            be_read = True
        if be_read and line[:15] == ' Total CPU time':
            linesplit = line.split()
            time_cpu = float(linesplit[-4])
            time_wall = float(linesplit[-2])
            # if time_wall <0 or time_cpu <0:
            #     print(time_wall)
    if dtype == None:
        return LogData(info1, numIter, bePRE, beUNPRE, time_cpu, time_wall)
    elif dtype == dict:
        return dict(info1=info1, numIter=numIter, bePRE=bePRE, beUNPRE=beUNPRE,time_cpu=time_cpu, time_wall=time_wall)
    else:
        return dtype((info1, numIter, bePRE, beUNPRE,time_cpu, time_wall))



def extract_data(folder, name='output.log', dtype=None):
    '''
    Read data from a log file in a folder.
    Can give result in either class 'LogData', 'dict', 'tuple' and some others.
    :param dtype: If None, returns logs data in LogData type.
    '''
    filename =os.path.join(folder, name)
    with open(filename, 'r') as file:
        return _extract_data(file, dtype)


def extract_from_many_simple(parent_folder):
    subdir_log_dict = {}
    for subdir in subdirs(parent_folder):
        try:
            folder =os.path.join(parent_folder, subdir)
            log_dict = extract_data(folder, dtype=dict)
        except (FileNotFoundError, UnboundLocalError):
            continue
        subdir_log_dict[subdir] = log_dict
    df = pd.DataFrame.from_dict(subdir_log_dict, orient='index')
    return df


def _extract_from_many_folders(parent_folder, max_depth=3, depth=1, rel_path=""):
    '''
    Extract logs in subdolders of 'parent_folder',
    Tf a subdirectory doesn't have correct log file, go recursively into subfolders up to max_depth
    '''
    data_dict = {}
    for subdir in subdirs(parent_folder):
        relative_path =os.path.join(rel_path, subdir)
        folder =os.path.join(parent_folder, subdir)
        try:
            log_dict = extract_data(folder, dtype=dict)
            data_to_update = {str(relative_path): log_dict}
        except (FileNotFoundError, UnboundLocalError) as err:
            if depth < max_depth:
                data_to_update = _extract_from_many_folders(folder, max_depth, depth=depth + 1, rel_path=relative_path)
            else:
                data_to_update = {}
        data_dict.update(data_to_update)
    if depth > 1:
        return data_dict
    else:
        df = pd.DataFrame.from_dict(data_dict, orient='index')
        return df


def print_failed(folder, max_depth=3):
    df = extract_from_many(folder, max_depth=max_depth)
    count_total = df['numIter'].count()
    count_failed = df[df['numIter'] == 500]['numIter'].count()

    print('In folder {0}:'.format(folder))
    print('{0} FAILED to converge out of {1}'.format(count_failed, count_total))

#------hdf5 support-----

def extract_data_hdf5(group, name='log_raw', dtype=None):
    '''
    :param group: h5py.Group
    '''
    data = dict(group[name].attrs)
    if dtype == None:
        return LogData(**data)
    elif dtype == dict:
        return dict(**data)
    else:
        raise NotImplementedError
    # log_raw_str = group[name].value
    # with io.StringIO(log_raw_str) as file:
    #     return _extract_data(file, dtype=dtype)


def _extract_from_many_hdf5(group, max_depth=3, depth=1, rel_path=""):
    '''
    Extract logs in subdolders of 'parent_folder',
    If a subdirectory does not have correct log file, go recursively into subfolders up to max_depth
    '''
    import FBEM.myh5 as myh5
    data_dict = {}
    for key in myh5.subgroups_names(group):
        relative_path = path_to_string(os.path.join(rel_path, key))
        try:
            log_dict = extract_data_hdf5(group[key], dtype=dict)
            data_to_update = {str(relative_path): log_dict}
        except KeyError as err:
            if depth < max_depth:
                data_to_update = _extract_from_many_hdf5(group[key], max_depth, depth=depth + 1, rel_path=relative_path)
            else:
                data_to_update = {}
        data_dict.update(data_to_update)
    if depth > 1:
        return data_dict
    else:
        df = pd.DataFrame.from_dict(data_dict, orient='index')
        return df

# ----- Both hdf5 and text formats

def extract_from_many(path, max_depth, group=''):
    '''
    :param path: either folder or hdf5 filename
    :param group: group in hdf5 file; ignored if `path` is a folder
    '''
    path = Path(path)
    group = path_to_string(group)
    if not path.exists():
        raise ValueError("Path doesn't point to a hdf5 file or a directory")
    if path.is_dir():
        df = _extract_from_many_folders(path, max_depth)
    elif path.suffix in ['.h5', '.hdf5']:
        import h5py
        with h5py.File(path) as f:
            g = f[group]
            df = _extract_from_many_hdf5(g, max_depth)
    else:
        raise NotImplementedError

    return df