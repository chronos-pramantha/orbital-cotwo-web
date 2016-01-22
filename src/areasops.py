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
from src.spatial import spatial


class Controller:
    """
    Processing Model. Business Layer. Business Logic.

    Take a POINT or a POLYGON EWKT and perform the magic.
    It get created at each request to handle the procedure of
    aggregating and returnig Xco2 to the client.
    """
    elements = ('POINT', 'POLYGON', )

    def __init__(self, geometry):
        if any(geometry.find(e) != -1 for e in self.elements):
            self.element = [e for e in self.elements if geometry.find(e) != -1][0]
        else:
            raise ValueError('Controller: geometry has to be '
                             'a EWKT POINT or POLYGON')
        self.geometry = geometry

    @property
    def is_view(self):
        """
        Check if a polygon is a single AoI or a multiple AoI (View).
        If the Controller is a point is False.
        :return bool:
        """
        return False

    @property
    def pk(self):
        """
        Return the primary key of the Controller's geometry if exist,
        else fallback in look_for_closest_point()
        :return int: pk
        """
        # if it's a point, check t_areas.center and t_co2.geometry
        # if it's a polygon, check t_areas.aoi
        # else is a View, create a View (a collection of AoI in the same map view) object
        return 1

    @property
    def center(self):
        """
        Return the point itself or the center of the polygon.
        :return:
        """
        # if it's a point, return the point
        # if it's a polygon, calculate and return the center of the polygon
        # else is a View, create a View (a collection of AoI in the same map view) object
        return 1

    @classmethod
    def is_point_in_any_area(cls, point):
        """
        Find the area the geometry belong to, if nay in the database.

        Just an easier accessor for AreasOps.get_aoi_that_contains_().

        :return tuple: (False, None) or (True, (object_tuple,))
        """
        query = select([Areas]).where(func.ST_Contains(Areas.aoi, point))
        print(str(query.compile()))
        result = areasOps.exec_func_query(query, multi=False)
        if not result:
            return False, None
        return True, result

    @classmethod
    def what_are_the_closest_centers_to_(cls, point):
        """
        Returns the 3 closest area's centers from a point.
        :param point: a EWKT geometry
        :return list: of 3 centers in the t_areas table
        """
        pass

    def which_areas_contains_this_polygon(self):
        """
        Return the list of areas contained by the controller's polygon
        :return generator: ResultProxy
        """
        query = select([Areas]).where(func.ST_Contains(self.polygon, Areas.aoi))
        print(str(query.compile()))
        results = areasOps.exec_func_query(query, multi=True)
        return results

    def which_points_contains_this_area(self):
        """
        Return the list of points contained by this area
        :return generator: ResultProxy
        """
        query = select([Xco2]).where(func.ST_Contains(self.polygon, Xco2.geometry))
        print(str(query.compile()))
        results = areasOps.exec_func_query(query, multi=True)
        return results


class areasOps(dbProxy):
    """
    All DB operations connected to areaAlgorithm calculations and storages.
    Also include DB operations on Xco2 table.

    Part of Database Manipulation Layer.

    """
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
        # return the row with added the EWKT representation of the AoI
        result = cls.alchemy.execute(
            'SELECT id, aoi, center, data, ST_AsEWKT(aoi) '
            'FROM t_areas WHERE ST_contains(t_areas.aoi, %s);',
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
        :return object: Controller object
        """
        area, center = spatial.shape_aoi(center)
        points = cls.find_all_points_in_(area)
        geojson = cls.serialize_geojson(
            points
        ) if len(points) != 0 is not None else cls.initialize_geojson(center)
        ins = Areas.__table__.insert().values(
            aoi=area,
            center=center,
            data=geojson
        )
        cls.alchemy.execute(ins)
        return Controller(area)

    @classmethod
    def update_aoi_geojson(cls, geometry, aoi, xco2):
        """Prototype: should update AoI data without recreating the full json"""
        # unpack row
        pk, aoi, center, data, ewkt = aoi
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
        return Controller(ewkt)

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
            x, y = spatial.unshape_geo_hash(p[3])
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
        x, y = spatial.unshape_geo_hash(point)
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

        :param str area: an Controller object
        :return tuple: database results
        """
        # find all points in Xco2 that belong to area
        result = cls.alchemy.execute(
            'SELECT * FROM t_co2 WHERE ST_contains(%s, t_co2.geometry);',
            (area, )
        ).fetchall()
        return result

    @classmethod
    def exec_func_query(cls, query, multi=False):
        """
        Run a PostGIS query using SQLAlchemy cursor.

        Example:
            >>> from sqlalchemy import func
            >>> query = select([Xco2.id, func.ST_AsGEOJSON(Xco2.coordinates)]).where(Xco2.id == 1)
            >>> print(str(query.compile()))
            >>> self.exec_func_query(query)

        :param str query: a custom query string or a SQLAlchemy construct (select())
        :param bool multi: set it to True if you expect multiple rows
        :return tuple: data contained in required columns
        """
        proxy = cls.alchemy.execute(query)
        return proxy.first() if not multi else proxy.fetchall()
