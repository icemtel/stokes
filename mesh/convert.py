'''
- Convert rule to mesh (c, v, t)
- Convert system to mesh (triangulation object)
'''

import numpy as np
import mesh.shapes as shapes
from mesh import prepare_system


## Function to convert system to Triangulation
def triangulate_system(*tria_generator_args, tria_generator=None, external_flow_field=None):
    '''
    EXAMPLE:
    sphere = create_sphere(..)
    system = prepare_system(sphere)
    triangulation = triangulate_system(system)

    :param tria_generator_args: by default - only system
    :param external_flow_field:
    :return: Triangulation object
    '''
    if tria_generator is None:
        tria_generator = fuse_mesh
    triangulation = tria_generator(*tria_generator_args)
    if external_flow_field is not None:
        triangulation = add_external_flow_field(triangulation, external_flow_field)
    return triangulation


def fuse_mesh(system):
    """
    system is a convert, constructed by FMM.meshObject.transformed_shape.
    return an object with:
        self.coordinates
        self.velocities
        self.triangulation
        self.coordRanges
        self.triaRanges
    """
    # for rules2meshes to work, the system must be wrapped up in a dictionary
    # exactly one key value pair
    system = prepare_system(system)
    system = {'all': system}
    # the rules, given as dictionaries with a 'type' key (plane, flagellum,
    # ellipsoid) are transformed to meshes
    meshes = rules2meshes(system)
    # those meshes are then orgaized in a tree structure, given by the
    # mesh.Triangulation.System class
    mesh_system = meshes2system(meshes)
    # velocity, angular velocity, rotation and translation of nodes of the
    # tree above are performed.
    mesh_system.adapt()
    # the System tree is fused into a flat array of coordinates, velocities and
    # the triangulation
    return mesh_system.fuse()


## Helper functions
def add_external_flow_field(mesh, flow):
    '''
    Wasn't tested yet - might be useful later.
    '''
    for (r, v) in zip(mesh.coordinates, mesh.velocities):
        v += flow(r)
    return mesh


def rules2meshes(rules):
    """
    recursively obtain meshes from rules.
    """
    from copy import deepcopy
    res = deepcopy(rules)
    for r in rules:
        if 'type' in rules[r]['system']:
            res[r]['system'] = meshProductionRule2Mesh(rules[r]['system'])
        else:
            res[r]['system'] = rules2meshes(rules[r]['system'])
    return res


def meshes2system(meshes):
    """
    recursively generate system.
    """
    from mesh.Triangulation import TrivialSystem, ComposedSystem, State
    firstKey = list(meshes.keys())[0]
    mm = meshes[firstKey]
    state = State(translation=mm['translate'],
                  rotation=mm['rotate'],
                  velocity=mm['velocity'],
                  angular=mm['angular'])
    if 'triangulation' in mm['system']:
        return TrivialSystem(coordinates=mm['system']['coordinates'],
                             velocities=mm['system']['velocities'],
                             triangulation=mm['system']['triangulation'],
                             state=state,
                             id=firstKey)
    else:
        return ComposedSystem(state=state,
                              subsystems=[meshes2system({m: mm['system'][m]}) for m in mm['system']],
                              id=firstKey)


##  Transform a single object (rule)
def meshProductionRule2Mesh(rule):
    """
    When making new rule:
    (1) Triangulation numbering starts from 0, then it will be automatically changed to start from 1 in FBEM files
    (2) Triangulation has to be oriented in correct way.

    rule is a dictionary, with a key 'type', corresponding to one of the types of meshable objects.
    returns a dictionary of lists of triples, representing coordinates,
    velocities and triangulation.
    Returns dictionary with coordinates, velocities and triangulation - each entry is scipy array;
    """

    if rule['type'] == 'ellipsoid':  # Position of Ellipsoid is saved earlier with 'transform'
        (c, v, t) = shapes.prepareEllipsoid(lengths=rule['lengths'],
                                            axe1=rule['axe1'],
                                            axe2=rule['axe2'],
                                            grid=rule['grid'])

    elif rule['type'] == 'flagellum':
        (c, v, t) = shapes.prepareFlagella(radius=rule['radius'],
                                           points1=rule['positions'],
                                           points2=rule['future positions'],
                                           nTheta=rule['azimuth grid'],
                                           dt=rule['dt'])
    elif rule['type'] == 'flat_ellipse':
        (c, v, t) = shapes.prepareFlatEllipse(**rule)

    elif rule['type'] == 'plane':
        (c, v, t) = shapes.preparePlane(p0=rule['p0'],
                                        p1=rule['p1'],
                                        p2=rule['p2'],
                                        width=rule['width'],
                                        grid1=rule['grid1'],
                                        grid2=rule['grid2'],
                                        centers=rule['centers'])

    elif rule['type'] == 'cuboid':
        (c, v, t) = shapes.prepareCuboid(**rule)

    elif rule['type'] == 'flagellumVel':
        (c, v, t) = shapes.prepareFlagellaVel(**rule)

    elif rule['type'] == 'flagellumVelNorm':
        (c, v, t) = shapes.prepareFlagellaVelNorm(**rule)

    elif rule['type'] == 'flagellum2':
        (c, v, t) = shapes.prepareFlagella2(**rule)


    # !!!! Find other object types in GK's code:
    #
    # elif rule['type'] == 'bacterial head':
    #     (c, v, t) = prepareBacterialHead(length=rule['length'],
    #                                      radius=rule['radius'],
    #                                      grid=rule['grid'])
    #
    # elif rule['type'] == 'worm':
    #     (c, v, t) = prepareWorm(radius=rule['radius'],
    #                             points1=rule['positions'],
    #                             points2=rule['future positions'],
    #                             nTheta=rule['azimuth grid'],
    #                             dt=rule['dt'])
    # elif rule['type'] == 'flatplane':
    #     (c, v, t) = preparePlane_old(p0=rule['p0'],
    #                                  p1=rule['p1'],
    #                                  p2=rule['p2'],
    #                                  grid1=rule['grid1'],
    #                                  grid2=rule['grid2'],
    #                                  centers=rule['centers'])
    #
    # elif rule['type'] == 'flowing plane':
    #     (c, v, t) = prepareFlowingPlane(p0=rule['p0'],
    #                                     p1=rule['p1'],
    #                                     p2=rule['p2'],
    #                                     grid1=rule['grid1'],
    #                                     grid2=rule['grid2'],
    #                                     centers=rule['centers'],
    #                                     velocity_field=rule['velocity_field'])

    else:
        raise NotImplementedError('Not recognized type of object to mesh. Check GK code for some more objects')

    return {'coordinates': np.array(c),
            'velocities': np.array(v),
            'triangulation': np.array(t, dtype=np.uint)}  # unsigned integer
