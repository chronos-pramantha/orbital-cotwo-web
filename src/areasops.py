# coding=utf-8
"""
Extends Areas to provide methods to apply the algorithm to properly
populate the t_areas table.
"""
from sqlalchemy import select, func
__author__ = 'Lorenzo'

from src.xco2 import Areas, Xco2
from src.dbops import dbProxy
from src.spatial import spatialRef


class areasOps(Areas):
    """
    When a client requests a center `(x, y)`, the lookup table can find the square
    containing that point and respond with the JSON. (If a point is not in any square,
    the algorithm looks on the areas of the closest (in a 200 Km radius) centers to
    the point, or generate a new area with this point as a center).

    The outcome is a big array of point that has to be turned into a set of tuples (probably
    around 1500 elements), then serialized into a GEOJSON and stored in the proper column.
    """
    def is_point_in_any_area(self, point):
        """
        Return the area that contains a point.

        :param point:
        :return:
        """
        point = Xco2.shape_geometry(point[0], point[1])
        table = Areas
        query = select(
            [table.id, func.ST_Contains(table.aoi, point)]
        )
        spatialRef.exec_func_query(query)
        pass

    def what_are_the_closest_centers_to_(self, point):
        """
        Returns the closest area's centers from a point.
        :param point:
        :return: array of points in the t_areas table
        """
        pass

    def which_areas_contains_this_(self, points):
        """
        Return the areas
        :param point:
        :return: arrays of areas in the t_areas table
        """
        pass


class areasDbOps(dbProxy):
    """
    All DB operations connected to AoI calculation and storage.
    Also include DB operations on Xco2 table.

    """
    def store_or_update_json(self, data):
        """
        Store a GEOJSON from the results of a query in the t_co2 table.

        :param data:
        :return:
        """
        pass

    def find_all_points_in_(self, area):
        """
        Fetch all the points in t_co2 contained by a given area.
        :param area:
        :return:
        """
        pass

    def fetch_json_for_a_(self, area_or_center):
        """
        Retrieve the JSON data for a center/area.
        :param area_or_center:
        :return:
        """
        pass