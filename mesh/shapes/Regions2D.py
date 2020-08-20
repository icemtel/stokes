import numpy as np
import scipy.linalg as lin
import mesh.triangulate2D as t2D


class _RefinementBase:
    def produce_mesh(self):
        raise NotImplementedError

    def produce_boundary_points(self):
        raise NotImplementedError

    def distance_to_point(self, point):
        raise NotImplementedError

    def distance_to_region(self, region):
        raise NotImplementedError


class RefinementCircle(_RefinementBase):
    def __init__(self, xy, radius, max_area):
        """
        xy: tuple/sp.array with coordinates
        max_area - max area parameter in
        """
        self.center = np.array(xy)
        self.radius = radius
        self.max_area = max_area

    def produce_mesh(self):
        coords, trias = t2D.triangulate_circle(self.center, self.radius, self.max_area)
        return coords, trias

    def produce_boundary_points(self):
        n_circle = t2D.get_number_of_circle_points2(self.radius, self.max_area)
        coords = t2D.points_on_ellipse(n_circle, self.radius, self.radius, center=center)
        return coords

    def distance_to_point(self, point):
        return max(lin.norm(self.center - point) - self.radius, 0)

    def distance_to_region(self, region):
        '''
        :param region: Other refinement region
        :return:
        '''
        dist_region_to_center = region.distance_to_point(self.center)
        dist_region_to_circle = max(dist_region_to_center - self.radius, 0)
        return dist_region_to_circle

class RefinementNestedCircles(_RefinementBase):
    def __init__(self, xy, radii, max_areas, subregions=None):
        '''
        :param xy:  tuple/sp.array with coordinates of the center
        :param radii: list of circle radii
        :param max_areas: list of max_areas, corresponding to each of the circles
        :param subregions: single subregion, or a list of subregions, which lie inside
        - it will get meshed, and points included to the combined region
        '''
        self.center = np.array(xy)
        sorted_index = sorted(range(len(radii)), key=lambda k: radii[k]) # sort radii; return index
        self.radii = np.array(radii)[sorted_index]
        self.max_areas = np.array(max_areas)[sorted_index]
        if subregions is not None:
            if isinstance(subregions, _RefinementBase): # if subregions is just one region
                self.subregions = subregions
            else: # if subregions is a list of regions
                self.subregions = RefinementMany(subregions)
        else:
            self.subregions = None

    def produce_mesh(self):
        ## Initial points - either from subregions, or None
        if self.subregions is not None:
            coords, trias = self.subregions.produce_mesh()
        else:
            coords= None
        # Mesh each of the nested circles with the corresponding max_area
        for radius, max_area in zip(self.radii, self.max_areas):
            coords, trias = t2D.triangulate_circle(self.center, radius, max_area, add_points=coords)
        return coords, trias

    def produce_boundary_points(self):
        n_circle = t2D.get_number_of_circle_points2(self.radii[-1], self.max_areas[-1])
        coords = t2D.points_on_ellipse(n_circle, self.radii[-1], self.radii[-1], center=center)
        return coords

    def distance_to_point(self, point):
        return max(lin.norm(self.center - point) - self.radii[-1], 0)

    def distance_to_region(self, region):
        '''
        :param region: Other refinement region
        :return:
        '''
        dist_region_to_center = region.distance_to_point(self.center)
        dist_region_to_circle = max(dist_region_to_center - self.radii[-1], 0)
        return dist_region_to_circle


class RefinementEllipse(_RefinementBase):
    def __init__(self, xy, lengths, max_area, rotation=0.):
        """
        xy: tuple/sp.array with coordinates
        max_area - max area parameter in
        """
        self.center = np.array(xy)
        self.lengths = lengths
        self.max_area = max_area
        self.rotation = rotation


    def produce_mesh(self):
        coords, trias = t2D.triangulate_ellipse(self.center, self.lengths, self.max_area, self.rotation)
        return coords, trias

    def produce_boundary_points(self):
        n_boundary = t2D.get_number_of_boundary_points_ellipse(self.lengths, self.max_area)
        coords = t2D.points_on_ellipse(n_boundary, self.lengths[0], self.lengths[1], self.rotation, self.center)
        return coords

    def distance_to_point(self, point):
        boundary_points = self.produce_boundary_points()
        return np.amin(lin.norm(boundary_points - point, axis=1))

    def distance_to_region(self, region):
        '''
        :param region: Other refinement region
        :return:
        FIXME: This function returns positive values if two regions intersect! - Check if boundary segments of two regions intersect or not
        '''
        boundary_points = self.produce_boundary_points()
        dist_to_boundary = np.amin([region.distance_to_point(bp) for bp in boundary_points])
        return dist_to_boundary


class RefinementMany(_RefinementBase):
    def __init__(self, list_of_refinements):
        self.list_of_refinements = list_of_refinements

    def produce_mesh(self):
        # Check that regions do not intersect
        for i, region1 in enumerate(self.list_of_refinements):
            for region2 in self.list_of_refinements[i + 1:]:
                dist = region1.distance_to_region(region2)
                if dist == 0:
                    raise NotImplementedError('Refinement regions collide!')
                    # TODO: Change procedure if two regions collide
        #                   # TODO: what if a region touches outer boundary?
        points_list = []
        trias_list = []
        trias_start_id = 0
        for refinement in self.list_of_refinements:
            points, trias = refinement.produce_mesh()
            points_list.append(points)
            trias = trias + trias_start_id  # shift all triangulation numbers, to account for the previously added points
            trias_list.append(trias)
            trias_start_id += len(points)
        if points_list == []:
            points_final = []
            trias_final = []
        else:
            points_final = np.concatenate(points_list)
            trias_final = np.concatenate(trias_list)
        return points_final, trias_final

    def distance_to_point(self, point):
        min_dist = np.inf
        for refinement in self.list_of_refinements:
            dist = refinement.distance_to_point(point)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def disntace_to_region(self, region):
        '''
        :param region: Other refinement region
        :return:
        '''
        min_dist = np.inf
        for refinement in self.list_of_refinements:
            dist = refinement.distance_to_region(region)
            if dist < min_dist:
                min_dist = dist
        return min_dist


if __name__ == '__main__':
    '''
    Some tests
    
    '''
    import matplotlib.pyplot as plt

    # #1 One circle
    # xy = 5, 4
    # radius = 7
    # max_area = 10
    # region = RefinementCircle(xy, radius, max_area)
    # coords, trias = region.produce_mesh()

    # #2 Many circles
    #
    # centers = [(0, 0), (0, 10), (10, 0)]
    # radii = [1, 2, 4]
    # max_areas = [0.1, 0.2, 0.4]
    # circles = []
    # for i, center in enumerate(centers):
    #     circles.append(RefinementCircle(center, radii[i], max_areas[i]))
    #
    # region = RefinementMany(circles)
    #
    # coords, trias = region.produce_mesh()
    #
    #
    # # Plot
    # import quick
    # with quick.Plot() as qp:
    #     xs, ys = coords[:, 0], coords[:, 1]
    #     qp.plot(xs, ys, 'o')
    #     qp.triplot(xs, ys, trias, color='orange')
    #
    #     qp.set_aspect('equal', adjustable='datalim')

    # 3 Ellipse
    # centers = [(0, 0), (0, 10)]
    # length_tuples = [(2, 1), (20, 4)]
    # max_areas = [0.5, 0.6]
    # rotations = [0, 0]
    # elis = []
    # for i, center in enumerate(centers):
    #     elis.append(RefinementEllipse(center, length_tuples[i], max_areas[i], rotations[i]))
    #
    # print(elis[0].distance_to_region(elis[1]))
    #
    # region = RefinementMany(elis)
    #
    # coords, trias = region.produce_mesh()

    # 4  Nested Circles
    center = (0,0)
    radii = (2, 5, 20)
    max_areas = (0.5, 2, 8)

    region = RefinementNestedCircles(center, radii, max_areas)

    coords, trias = region.produce_mesh()

    # Plot
    xs, ys = coords[:, 0], coords[:, 1]
    plt.plot(xs, ys, 'o')
    plt.triplot(xs, ys, trias, color='orange')

    plt.set_aspect('equal', adjustable='datalim')
    plt.show()

