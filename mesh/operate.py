'''
Operations on dictionaries, describing the geometrical system
'''
import numpy as np


def wrap(**names_and_systems):
    '''
    e.g. wrap(cilia=my_system) -> {'cilia': transform(my_system)}
    '''
    wrapped = {}
    for key in names_and_systems:
        wrapped[key] = transform(names_and_systems[key])
    return wrapped


def join_systems(*systems):
    '''
    Systems are dictionaries of form {'sphere1': ..}
    Raise a error if dictionary have a different form.
    Don't raise error if system is `None` - just skip it.
    '''
    joined_system = {}
    for system in systems:
        if system is None:
            continue
        if 'system' in system.keys():
            raise NotImplementedError # TODO: join unnamed systems (system that were just transformed)
        else:
            joined_system.update(system)
    return joined_system



def transform(system, translation=(0, 0, 0), rotation=np.diag([1, 1, 1]),
              velocity=(0, 0, 0), angular=(0, 0, 0)):
    '''
    From Gary's code - function to prescribe transformation rules to the system. Also used to 'wrap' the system.
    '''
    return {'system': system,
            'rotate': rotation,
            'translate': translation,
            'velocity': velocity,
            'angular': angular}


def prepare_system(system):
    '''
    The last step before passing the dictionary to GK's code which builds triangulations.
    Don't have to use this function manually - it will be called by write_input in stokes.FBEM
    '''
    if 'system' in system.keys():
        return system
    else:
        return transform(system)
