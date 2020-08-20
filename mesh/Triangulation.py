'''
- Define `Triangulation` object
- Initial contribution by Gary Klindt
'''
from numpy import dot, cross, concatenate, zeros, sum
from functools import reduce


class State(object):
    def __init__(self, **kwargs):
        self.translation = kwargs['translation']
        self.rotation = kwargs['rotation']
        self.velocity = kwargs['velocity']
        self.angular = kwargs['angular']
        # self.originshift = (0, 0, 0)


def fuseTwoRanges(range1, range2):
    return (min(range1[0], range2[0]), max(range1[1], range2[1]))


def fuseRanges(ranges):
    return reduce(fuseTwoRanges, list(ranges))


class Triangulation(object):
    def __init__(self, id=None,
                 coordinates=None,
                 velocities=None,
                 triangulation=None):
        self.coordinates = coordinates
        self.velocities = velocities
        self.triangulation = triangulation
        if coordinates is not None:
            self.coordRanges = {id: (0, len(coordinates) - 1)}
            self.triaRanges = {id: (0, len(triangulation) - 1)}
        else:
            self.coordRanges = None
            self.triaRanges = None

    def __iadd__(self, triangulation=None):
        """
        triangulation is a Triangulation object.
        The method changes self inplace and represents the fusion of self
        and triangulation.
        """
        # assume, that ranges are contiguous and start at 0

        coordMax = fuseRanges(self.coordRanges.values())[1]
        for r in triangulation.coordRanges:
            r0 = coordMax + triangulation.coordRanges[r][0] + 1
            r1 = coordMax + triangulation.coordRanges[r][1] + 1
            self.coordRanges[r] = (r0, r1)

        triaMax = fuseRanges(self.triaRanges.values())[1]
        for r in triangulation.triaRanges:
            r0 = triaMax + triangulation.triaRanges[r][0] + 1
            r1 = triaMax + triangulation.triaRanges[r][1] + 1
            self.triaRanges[r] = (r0, r1)
        # from the previous, it follows, that there is no overlap of ranges

        self.velocities = concatenate([self.velocities,
                                       triangulation.velocities])
        self.coordinates = concatenate([self.coordinates,
                                        triangulation.coordinates])
        hTria = zeros((len(self.triangulation) + len(triangulation.triangulation), 3))
        hTria[:len(self.triangulation), :] = self.triangulation
        for i in range(len(triangulation.triangulation)):
            hTria[i + triaMax + 1, 0] = triangulation.triangulation[i, 0] + coordMax + 1
            hTria[i + triaMax + 1, 1] = triangulation.triangulation[i, 1] + coordMax + 1
            hTria[i + triaMax + 1, 2] = triangulation.triangulation[i, 2] + coordMax + 1
        self.triangulation = hTria
        return self

    def addId(self, id):
        fusedCoordRange = fuseRanges(self.coordRanges.values())
        fusedTriaRange = fuseRanges(self.triaRanges.values())
        self.coordRanges[id] = fusedCoordRange
        self.triaRanges[id] = fusedTriaRange

    def centered_at(self, id):
        """
        return an instance of Triangulation, which is the same as self, but
        translated such that the object denoted by id is in the origin.
        """
        origin = self.center_of(id)
        tria = Triangulation()
        tria.coordinates = self.coordinates - origin
        tria.velocities = self.velocities
        tria.triangulation = self.triangulation
        tria.coordRanges = self.coordRanges
        tria.triaRanges = self.triaRanges
        return tria

    def center_of(self, id):
        """
        return the center of mass of a submesh given by id.
        """
        (i_a, i_e) = self.coordRanges[id]
        coord_sum = sum(self.coordinates[i_a:i_e], axis=0)
        return coord_sum / len(self.coordinates)


class System(object):
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.state = kwargs['state']


class TrivialSystem(System):
    """
    it is assumed, that the system in its unadapted state is in the origin.
    We can do better: get the origin, move the coordinates, and change the state
    accordingly.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coordinates = kwargs['coordinates']
        # origin = np.sum(self.coordinates, axis=0) / len(self.coordinates)
        # self.coordinates -= origin
        # self.state.originshift = origin
        self.velocities = kwargs['velocities']
        self.triangulation = kwargs['triangulation']
        self.coordNum = len(self.coordinates)
        self.triaNum = len(self.triangulation)

    def adaptVelocity(self, state):
        for i in range(self.coordNum):
            direction = cross(state.angular, self.coordinates[i])
            rotation = dot(state.rotation, self.velocities[i])
            self.velocities[i] = rotation + state.velocity + direction

    def adaptRotation(self, state):
        for i in range(self.coordNum):
            self.coordinates[i] = dot(state.rotation, self.coordinates[i])

    def adaptTranslation(self, state):
        self.coordinates += state.translation

    def adaptOriginshift(self, state):
        self.coordinates += state.originshift

    def adapt(self):
        self.adaptMore([self.state])

    def adaptMore(self, states):
        for state in states:
            # self.adaptOriginshift(state)
            self.adaptRotation(state)
            self.adaptVelocity(state)
            self.adaptTranslation(state)

    def getSubsystemById(self, id):
        if self.id == id:
            return self

    def fuse(self):
        # print('  < ', self.id)
        return Triangulation(id=self.id,
                             coordinates=self.coordinates,
                             velocities=self.velocities,
                             triangulation=self.triangulation)


class ComposedSystem(System):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subsystems = kwargs['subsystems']

    def adaptMore(self, states):
        for s in self.subsystems:
            s.adaptMore([s.state] + states)

    def adapt(self):
        self.adaptMore([self.state])

    def isTrivial(self):
        return False

    def isComposed(self):
        return True

    def getSubsystemById(self, id):
        if self.id == id:
            return self
        for s in self.subsystems:
            return s.getSubsystemById(id)

    def fuse(self):
        # print('---', self.id)
        trias = [s.fuse() for s in self.subsystems]
        for i in range(len(trias) - 1):
            trias[0] += trias[i + 1]
        trias[0].addId(self.id)
        return trias[0]
