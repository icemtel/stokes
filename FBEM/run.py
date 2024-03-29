import sys
import subprocess
import logging
import os
import FBEM.write_input as write


# Default location of the executable file
if os.name == 'posix': # Linux
    exe_path = os.path.dirname(__file__) +  '/exe/3D_Stokes_Flow_FMM_linux.exe'
else: # Windows
    exe_path = os.path.dirname(__file__) +  '/exe/3D_Stokes_Flow_FMM_64.exe'

def run(system, folder, params=None, exe_path=exe_path):
    '''
    :param system: system - a dictionary, as generated by `mesh` package
    :param folder: location of input and output files
    :param params: dictionary with parameters; to generate input.cnd;
    :param exe_path: Path to FBEM executable
    :return: None
    '''
    os.makedirs(folder, exist_ok=True) # create folder
    write.write_input_cnd(folder, params) # write input file
    write.write_input_and_ranges(folder, system)
    logging.info("Success: Create FBEM input files")

    run_from_input(folder, exe_path=exe_path)
    remove_plt(folder)  # To save storage space


def run_from_input(folder='.', exe_path=exe_path):
    '''
    Runs FBEM with input files already written to folder.

    If running on linux with threading - assign a single core for each process
    (otherwise FBEM will try to use up every core)
    '''
    # If on Linux, and threading is enabled, limit each FBEM process to a single core.
    if 'threading' in sys.modules and os.name == 'posix':
        import threading
        if threading.current_thread() == threading.main_thread():
            call_until_success(exe_path, working_dir=folder)
        else:
            thread_name = threading.current_thread().name
            cpu_id = str(int(thread_name[-1]) -1)  # e.g. Thread-1 => cpu_id = 0
            command = ["taskset", "-c", cpu_id,exe_path]
            call_until_success(command, working_dir=folder)
    else:  # Windows executable works only in one process, so we don't have to limit it.
        call_until_success(exe_path, working_dir=folder)
    logging.info("Success: FBEM run")


# ----- Helpers functions ------
def remove_plt(folder):
    '''
    Removes output.plt file, as it only duplicates the information from output.dat
    '''
    name = 'output.plt'
    os.remove(os.path.join(folder, name))


def count_lines(filename):
    try:
        filehandle = open(filename, 'r')
        number = len(filehandle.readlines())
        filehandle.close()
        return number
    except:
        return 0


def call_until_success(exe_path, working_dir=None):
    # Run FBEM, redirect stdout
    # Otherwise contents of output.log will be printed to stdout.
    # Maybe should redirect stderr to somewhere I can trace it?
    with open(os.devnull, 'w') as devnull:
        completedProcess = subprocess.run(exe_path, cwd=working_dir, stdout=devnull, stderr=None)

    if completedProcess.returncode == 1:
        logging.error('call_until_success: Error executing the process %s', exe_path)
    # If output file is too short, restart
    if count_lines(os.path.join(working_dir, 'output.dat')) < 10:
        logging.error('FBEM log file is too short, restarting...')
        return call_until_success(exe_path, working_dir)
