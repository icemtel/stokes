import time
import datetime
import math
import os

def print_out(*args):
    return print(*args)


def evaluate(function_to_run, *args, input_space=None, **kwargs):
    '''
    Wrap a funciton which performs experiment.
    Measure and print how much time it spends
    Guess how much time needed to run all the simulations (multiply time to run one simulation by total number to run)

    Not Implemented:
        Track memory usage - too complicated; + need to take into account that FBEM is called as different process.
        Doesn't work well with recursive functions
    '''

    print_out("Start: evaluate function '{}'".format(function_to_run.__name__))
    print_out("    Input given: {0}".format(args))
    start = time.time()
    output = function_to_run(*args, **kwargs)
    finish = time.time()
    time_spent = finish - start
    print_out('    Time spent: ', datetime.timedelta(seconds=time_spent))
    if input_space != None:
        space_size = len(input_space)
        print_out('    Estimated time to run everything:', datetime.timedelta(seconds=space_size * time_spent),
                  "on one core")
    print_out("Finish: evaluate function '{}'".format(function_to_run.__name__))
    return output


def evaluate_and_assign_folder(function_to_run, *args, folder_generator=None, parent_folder=None, input_space=None, **kwargs):
    if parent_folder is None:
        parent_folder = 'tmp/'
    if folder_generator is None:
        timestr = time.strftime("testrun %Y-%m-%d %H.%M")
        folder = os.path.join(parent_folder, timestr)
    else:
        folder = os.path.join(parent_folder, folder_generator(*args, **kwargs))
    evaluate(function_to_run, *args, **kwargs, folder=folder, input_space=input_space)
    print('Folder generated:', folder)
    return folder


if __name__ == '__main__':
    """
    Test
    """


    def f(n):
        sum = 0
        for i in range(n):
            sum += math.log(n)
        return sum


    evaluate(f, n=500570, input_space=range(100))


    def f_save(n, folder):
        sum = 0
        for i in range(n):
            sum += math.log(n + 1)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, 'out.dat'), 'w') as output:
            output.write(str(sum))


    evaluate_and_assign_folder(f_save, n=500570, input_space=range(100))
