import os
from pathlib import Path # a class to handle os paths

def prepare_csv_line(*entries, delimeter=","):
    '''
    Prepare a list of objects for writing into a csv file.
    '''
    line_str_list = map(str, entries)
    line = delimeter.join(line_str_list) + "\n"
    return line


def subdirs(folder):
    '''
    Takes string - path to a folder, returns a list of subfolders (strings).
    # os.listdir(folder )  - would also return file names in folder
    If there are no subdirectories, returns an empty array.
    '''
    try:
        a = next(os.walk(folder))
    except StopIteration:
        return []
    else:
        return a[1]

def path_to_string(path):
    '''
    Standard string representation of a path.
    '''
    return Path(path).as_posix()