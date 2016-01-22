# coding=utf-8
"""
Thia modulw contains a class that is a wrapper around Database data
 and a class that manage all the operations on the t_areas table.
"""
from collections import namedtuple
from sqlalchemy import select, func
import json
__author__ = 'Lorenzo'

from src.xco2 import Areas, Xco2
from src.dbproxy import dbProxy
from src.spatial import spatialOps


class areasAlgorithm:
    """
    When a client requests a center `(x, y)`, the lookup table can find the square
    containing that point and respond with the JSON. (If a point is not in any square,
    the algorithm looks on the areas of the closest (in a 200 Km radius) centers to
    the point, or generate a new area with this point as a center).

    The outcome is a big array of point that has to be turned into a set of tuples (probably
    around 1500 elements), then serialized into a GEOJSON and stored in the proper column.

    Hold the data and apply all the needed calculation for a complex database operation.

    It leverages the methods in the dataOps, spatialOps and areaOps classes.
    """
    def __init__(self, area, **kwargs):
        self.pk = area[0]
        self.geometry = area[1]
        self.center = area[2]
        # these below are all EWKT strings
        self.data = area[3]

    @property
    def is_point_in_any_area(self):
        """
        Find the area the geometry belong to, if nay in the database.

        Just an easier accessor for areasDbOps.get_aoi_that_contains_().

        :return tuple: (False, None) or (True, (object_tuple,))
        """
        return areasDbOps.get_aoi_that_contains_(
            self.geometry
        )

    @property
    def center_of_the_area(self):
        return self.center


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
    All DB operations connected to areaAlgorithm calculations and storages.
    Also include DB operations on Xco2 table.

    """
    @classmethod
    def store_area(cls, geometry, xco2):
        """
        Given a geometry of a stored point, it adds this point to an existing Area
        of Interest or stores a new AoI with center the given geoemtry.

        :param str geometry: a EWKT string for a geometry
        :return:
        """
        aoi = cls.get_aoi_that_contains_(geometry)
        if aoi.check is True:
            # add the point to the existing aoi
            aoi = cls.update_aoi_geojson(geometry, aoi.row, xco2)
        elif aoi.check is False:
            # create aoi with center geometry and new geojson, return it
            aoi = cls.store_new_aoi(geometry)
        else:
            raise ValueError('get_aoi_that_contains_(geometry) returned a wrong value '
                             'for key \'check\'. It can be only True or False')

        return aoi

    @classmethod
    def get_aoi_that_contains_(cls, geometry):
        """
        Check if SELECT * FROM t_areas WHERE ST_contains(area, geometry); is not empty

        :param str geometry: the EWKT representation of the geometry
        :return tuple: (bool, (result_object),)

        Return the area that contains a point.

        :return:
        """
        aoi = namedtuple('area', ['check', 'row'])
        result = cls.alchemy.execute(
            'SELECT * FROM t_areas WHERE ST_contains(t_areas.aoi, %s);',
            (geometry, )
        ).first()
        if result:
            boolean = True
        else:
            boolean = False
        return aoi(check=boolean, row=result)

    @classmethod
    def store_new_aoi(cls, center):
        """
        There is no area for this center, a new area is stored
        with center equal to this center.

        :param str center: a EWKT string of a point
        :return object: areasAlgorithm object
        """
        area, center = spatialOps.shape_aoi(center)
        points = cls.find_all_points_in_(area)
        geojson = cls.serialize_geojson(
            points
        ) if len(points) != 0 is not None else cls.initialize_geojson(center)
        ins = Areas.__table__.insert().values(
            aoi=area,
            center=center,
            data=geojson
        )
        result = cls.alchemy.execute(ins)
        return areasAlgorithm((result.inserted_primary_key[0], area, center, geojson))

    @classmethod
    def update_aoi_geojson(cls, geometry, aoi, xco2):
        """Prototype: should update AoI data without recreating the full json"""
        # unpack row
        pk, aoi, center, data = aoi
        # get [x, y] from EWKT
        point = [float(g) for g in geometry[16:-1].split(' ')]
        # append to JSON
        data['features'].append({
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": point
              },
              "properties": {
                "xco2": xco2
              }
            })
        upd = Areas.__table__.update().values(
            data=data
        ).where(Areas.id == pk)
        cls.alchemy.execute(upd)
        return areasAlgorithm((pk, aoi, center, data))

    @classmethod
    def serialize_geojson(cls, points_tuple):
        """
        Return a GeoJson from a sequence of tuples.

        :param points_tuple: a sequence of Xco2 points.
        :return: a GeoJSON with the co2 data for the points
        """
        geojson = {
            "features": []
        }
        for p in points_tuple:
            x, y = spatialOps.unshape_geo_hash(p[3])
            xco2 = p[1]
            # store initialized geojson with center
            # as the only feature-point
            geojson["features"].append({
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [x, y]
              },
              "properties": {
                "xco2": xco2
              }
            })
        return geojson


    @classmethod
    def initialize_geojson(cls, point):
        """
        Return a GeoJSON with only one point, the center of the AoI.

        :param point: a center point of a AoI
        :return: a GeoJSON containing only the center point
        """
        x, y = spatialOps.unshape_geo_hash(point)
        xco2 = cls._connected(
            'SELECT xco2 from t_co2 WHERE pixels = %s',
            **{
                'values': (point, )
            }
        )[0]
        # store initialized geojson with center
        # as the only feature-point
        return {
            "features": [{
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [x, y]
              },
              "properties": {
                "xco2": xco2
              }
            }]
        }

    @classmethod
    def find_all_points_in_(cls, area):
        """
        Query executor: fetch all the points in t_co2 contained by a given area.

        :param areasAlgorithm area: an areasAlgorithm object
        :return tuple: database results
        """
        # find all points in Xco2 that belong to area
        result = cls.alchemy.execute(
            'SELECT * FROM t_co2 WHERE ST_contains(%s, t_co2.geometry);',
            (area, )
        ).fetchall()
        return result


__all__ = [
    'add_point_or_create_geojson'
]