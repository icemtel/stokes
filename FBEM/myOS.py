"""
Some shortcuts for file-operations
"""
from contextlib import contextmanager
import os
import shutil
import pathlib

devnull = os.devnull  # open(os.devnull, 'w')


# Path operations
def Path(path, *paths):
    '''
    Shortcut for pathlib.Path object
    '''
    full_path = os.path.join(path, *paths)
    return pathlib.Path(full_path)


# Many of these operations, in principle, are replaced by Path methods.
def pathjoin(path, *paths, return_str=False):
    '''
    Once pathlib.Path object is defined, operator '/' can be used instead of this function.
    '''
    if return_str:
        return os.path.join(path, *paths)
    else:
        return Path(path, *paths)


def subdirs(folder):
    '''
    Takes string - path to a folder, returns a list (generator) of strings with names of subdirectories.
    # os.listdir(folder )  - would also return file names in folder
    Returns empty list if there are no subdirectories..
    '''
    try:
        a = next(os.walk(folder))
    except StopIteration:
        return []
    else:
        return a[1]


def abspath(path):
    return Path(os.path.abspath(path))


def dir_name(path):
    '''
    Use  myOS.dir_name(__file__) to get location of a file, where this code is function is run.
    Works like abspath, but removes the last part of the path.
    '''
    return Path(os.path.dirname(path))


# Working directory
def get_cwd():
    return Path(os.getcwd())


def change_dir(foldername, create=True):
    # Change current working directory. If create=True and directory doesn't exist, create it.
    if create:
        os.makedirs(foldername, exist_ok=True)
    os.chdir(foldername)


# Context managers - https://stackoverflow.com/questions/3012488/what-is-the-python-with-statement-designed-for

@contextmanager
def working_directory(path):
    '''
    Use with "with" statement to temporally change working directory:
    with working_directory("data/stuff"):
        pass
    '''
    current_dir = get_cwd()
    change_dir(path)
    try:
        yield
    finally:
        change_dir(current_dir)


from tempfile import TemporaryDirectory

temporary_directory = TemporaryDirectory


# File operations
def make_dir(foldername, exist_ok=True):
    return os.makedirs(foldername, exist_ok=exist_ok)

def copyfile(src, dst):
    return shutil.copyfile(src, dst)


def remove_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def remove(filename):
    os.remove(filename)


def archive(input, output, exist_ok=True):
    '''
    Input can be a directory
    output - filename without an extension
    '''
    import shutil
    if not exist_ok:
        output_name = Path(output).with_suffix('.zip')
        if os.path.isfile(output_name):
            raise ValueError("File already exists")

    shutil.make_archive(output, 'zip', input)


# System

def hybernate(delay=10):
    import time
    for k in range(delay):
        print("Hybernation in {0} seconds..".format(delay - k))
        time.sleep(1)
    os.system("shutdown.exe /h")
