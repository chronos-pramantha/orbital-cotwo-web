# coding=utf-8
"""
Thia module contains a class that is the main class of the server
 and a class that manage all the operations on the t_areas table.
 The t_areas table is the one required to serve the client.
"""
import json
from collections import namedtuple
from sqlalchemy import select, func
from pygeoif import from_wkt, Point, Polygon

__author__ = 'Lorenzo'

from src.xco2 import Areas, Xco2
from src.dbproxy import dbProxy
from src.spatial import spatial


class Controller:
    """
    Processing Model. Business Layer. Business Logic.

    Take a POINT or a POLYGON EWKT and perform the magic.
    It get created at each request to handle the procedure of
    aggregating and returning Xco2 to the client.
    """
    elements = ('POINT', 'POLYGON', )

    def __init__(self, geometry):
        try:
            if any(geometry.find(e) != -1 for e in self.elements):
                self.element = [e for e in self.elements if geometry.find(e) != -1][0]
            else:
                raise ValueError('Controller: geometry has to be '
                                 'a EWKT POINT or POLYGON')
        except Exception as e:
            raise ValueError('The value passed at Controller is not in the right format: {}'.format(
                    str(e)
                )
            )
        self.geometry = geometry                   # EWKT string
        self.geo_object = from_wkt(self.geometry)  # pygeoif object
        # #todo: implement descriptors
        self.results_proxy = None                  # variable to store the resulting areas
        self.geojson = None                        # variable to store the resulting geojson

    def __str__(self):
        return 'Controller View for {element!s} at coordinates {coords!r}'.format(
            element=str(self.element),
            coords=str(self.geometry)
        )

    @property
    def is_view(self):
        """
        Check if a polygon is a single AoI or a multiple AoI (View).
        If the Controller is a point is False.
        :return bool:
        """
        if isinstance(self.geo_object, Point):
            return False
        elif dbProxy.alchemy.execute(
                'SELECT count(*) FROM t_areas WHERE ST_Contains(%s, aoi)',
                ((self.geometry, ), )
             ).first() == 1:
            return False
        else:
            return True

    @property
    def pks(self):
        """
        Return the primary keys of the Controller's geometry if exist
        (area or center or closest centers)
        :return int: pk
        """
        # if it's a point, check t_areas.center and t_co2.geometry
        if isinstance(self.geo_object, Point):
            # check in a larger radius circle for closest center
            query = select([Areas.id]).where(Areas.center == self.geometry)
            result = areasOps.exec_func_query(query, multi=False)
            if result:
                return True, result
            else:
                closest = self.what_are_the_closest_centers_to_(self.geometry)
                return True, closest
        else:
            query = select([Areas.id]).where(func.ST_Contains(self.geometry, Areas.aoi))
            # print(str(query.compile()))
            result = areasOps.exec_func_query(query, multi=True)
            if not result:
                return False, None
            return True, result

    @property
    def center(self):
        """
        Return the point itself or the center of the polygon.
        :return:
        """
        if isinstance(self.geo_object, Point):
            # if it's a point, return the point
            closest = self.what_are_the_closest_centers_to_(self.geometry)[0]
        elif isinstance(self.geo_object, Polygon):
            # if it's a polygon, calculate and return the center of the polygon
            coords = self.geo_object.__geo_interface__['coordinates'][0]
            side = abs(coords[0][0]-coords[0][1])
            return spatial.shape_geometry(coords[0][0] + side/2, coords[0][1] - side/2)
        else:
            raise ValueError('cls.center() method: geometry can be only {}'.format(
                self.elements
            ))

    @classmethod
    def is_point_in_any_area(cls, point):
        """
        Find the area the geometry belong to, if any in the database.

        Just an easier accessor for AreasOps.get_aoi_that_contains_().

        :return tuple: (False, None) or (True, (object_tuple,))
        """
        query = select([Areas]).where(func.ST_Contains(Areas.aoi, point))
        #print(str(query.compile()))
        result = areasOps.exec_func_query(query, multi=False)
        if not result:
            return False, None
        return True, result

    @classmethod
    def what_are_the_closest_centers_to_(cls, point):
        """
        Returns the closest area's centers from a point.

        Algorithm:
            X -1
            Y +1
            X 1
            Y -1

        :param point: a EWKT geometry
        :return list: of centers in the t_areas table
        """
        # build a square of side 'size' degrees around the point
        mapping = {
            '0': (0, -3),
            '1': (1, 3),
            '2': (0, 3),
            '3': (1, -3)
        }

        def increasing_area(p, results='start', step=0):
            # check if square contains point
            # if not recursively increase the size
            if results != 'start' and results or step == 25:
                return results[0] if results else None

            print(p, step)
            query = select([Areas.center]).where(func.ST_Contains(Areas.aoi, p))
            #print(str(query.compile()))
            results = areasOps.exec_func_query(query, multi=True)
            lookup = from_wkt(p).__geo_interface__['coordinates']
            stepping = lookup
            for r in range(100):
                s = step - 4
                if mapping.get(str(s), None):
                    if step % 2 == 0:
                        stepping = (lookup[mapping.get('2')[0]] + mapping.get('2')[1], lookup[1])
                    else:
                        stepping = (lookup[0], lookup[mapping.get('3')[0]] + mapping.get('3')[1])
            step += 1
            new_point = spatial.shape_geometry(stepping[0], stepping[1])
            return increasing_area(new_point, results, step)

        return increasing_area(point)

    def which_areas_contains_this_polygon(self):
        """
        Return the list of areas contained by the controller's polygon
        :return generator: ResultProxy
        """
        query = select([Areas]).where(func.ST_Contains(self.geometry, Areas.aoi))
        print(str(query.compile()))
        self.results_proxy = areasOps.exec_func_query(query, multi=True)
        return self.results_proxy

    def which_points_contains_this_area(self):
        """
        Return the list of points contained by this area
        :return generator: ResultProxy
        """
        query = select([Xco2]).where(func.ST_Contains(self.geometry, Xco2.geometry))
        print(str(query.compile()))
        results = areasOps.exec_func_query(query, multi=True)
        return results

    def serialize_features_from_database(self):
        """
        Dump the features retrieved from the database into a GeoJSON
        :return str:
        """
        geojson = {
            "data_source": "NASA Orbital Carbon Observatory",
            "jpl_url": "http://oco.jpl.nasa.gov",
            "developed_by": "Pramantha Ltd",
            "pramantha_url": "http://pramantha.net",
            "features": []
        }
        for d in self.results_proxy:
            for f in d.data["features"]:
                geojson["features"].append(f)
        return json.dumps(geojson)


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
