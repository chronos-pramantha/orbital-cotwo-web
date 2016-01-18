# coding=utf-8
import psycopg2
from sqlalchemy import func, select

__author__ = 'Lorenzo'

from src.xco2 import Xco2, Areas
from src.dbops import dbProxy
from config.config import USER, PWD


class spatialRef(dbProxy):
    """
    Handle spatial read operations on the database.
    """
    @classmethod
    def shape_geometry(cls, long, lat):
        """Return a EWKT string representing a point, to be passed to
        `ST_GeomFromEWKT` PostGIS function"""
        return 'SRID=3857;POINT({long!s} {lat!s})'.format(
            long=long,
            lat=lat
        )

    @classmethod
    def shape_geography(cls, long, lat, mode='POINT'):
        """Return a EWKT string representing a point, to be passed to
        `ST_GeogFromText` PostGIS function"""
        return 'SRID=4326;{mode!s}({long!s} {lat!s})'.format(
            mode=mode,
            long=long,
            lat=lat
        )

    @classmethod
    def shape_aoi(cls, center):
        """Build a square around a center point, to define a Area of Interest:
        w: X - 0.5*width
        e: X + 0.5*width
        n: Y + 0.5*height
        s: Y - 0.5*height

        Reminder:
           Geography(SRID=4326)
           Geometry(SRID=3857)

        Example query to cast a EWKT string in Geometry type:
            SELECT 'SRID=3857;POLYGON(((-179.748110962 -22.8178), (-178.348110962 -22.8178),
            (-179.048 -22.1178405762), (-179.048 -23.5178405762), (-179.748110962 -22.8178), ))'::geometry;

        :return tuple: polygon's EWKT and center's EWKT
        """
        SIZE = 1.4  # polygon side = 1.4 degree
        polygon = []
        polygon.append([center[0] - 0.5*SIZE, center[1]])
        polygon.append([center[0] + 0.5*SIZE, center[1]])
        polygon.append([center[0], center[1] + 0.5*SIZE])
        polygon.append([center[0], center[1] - 0.5*SIZE])
        polygon.append([center[0] - 0.5*SIZE, center[1]])
        string = str()
        for i, p in enumerate(polygon):
            string += str(p[0]) + ' ' + str(p[1])
            if i != len(polygon) - 1:
                string += ', '

        shape = 'SRID=3857;POLYGON(({polygon}))'.format(
            polygon=string
        )

        return shape, cls.shape_geometry(center[0], center[1])

    @classmethod
    def unshape_geo_hash(cls, geohash, ):
        """Return a tuple of (long, lat, ) from a hashed geometry/geography.

        Example:
            SELECT ST_AsEWKT('0101000020110F0000000000C0A947264000000020BB9165C0');
            --------------------------------------------------
            SRID=4326;POINT(11.111065864563 -7.45048522949219)

        Possible outputs:
            ST_AsGEOJSON
            ST_AsText
            ST_X
            ST_Y

        :param geohash: the value of a Geometry or Geography column
        :return tuple: (longitude, latitude, )
        """
        return cls._connected(
            "SELECT ST_X(%s), ST_Y(%s)",
            **{'values': (str(geohash), str(geohash), )}
        )

    @classmethod
    def exec_func_query(cls, query, multi=False):
        """
        Run a PostGIS query using SQLAlchemy cursor.

        Example:
            >>> from sqlalchemy import func
            >>> from src.dbops import dbOps
            >>> query = select([Xco2.id, func.ST_AsGEOJSON(Xco2.coordinates)]).where(Xco2.id == 1)
            >>> print(str(query.compile()))
            >>> spatialRef.exec_func_query(query)

        :param str query: a custom query string or a SQLAlchemy construct (select())
        :param bool multi: set it to True if you expect multiple rows
        :return tuple: data contained in required columns
        """
        proxy = cls.alchemy.execute(query)
        return proxy.first() if not multi else proxy.fetchall()


__all__ = ['shape_geometry',
           'shape_geography']
