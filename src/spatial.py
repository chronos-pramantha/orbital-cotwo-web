# coding=utf-8
import psycopg2
from sqlalchemy import func, select

__author__ = 'Lorenzo'

from src.xco2 import Xco2
from src.dbops import DB, dbProxy
from config.config import USER, PWD


class spatialRef(dbProxy):
    """
    Handle spatial read operations on the database.
    """
    @classmethod
    def connection(cls):
        """Connect to the PostgreSQL database.  Returns a database connection."""
        return psycopg2.connect('postgresql://{}:{}@localhost/{}'.format(
                USER, PWD, DB
            )
        )

    @classmethod
    def _connected(cls, *args):
        """Wrap execute() function to open and close properly connection and cursor"""
        conn = cls.connection()
        cur = conn.cursor()
        cur.execute(args[0], args[1])
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result

    @classmethod
    def unshape_geo_hash(cls, hash, ):
        """Return a tuple of (lat, long, ) from a hashed geometry/geography.

        Example:
            SELECT ST_AsEWKT('0101000020110F0000000000C0A947264000000020BB9165C0');
            --------------------------------------------------
            SRID=4326;POINT(11.111065864563 -7.45048522949219)

        Outputs:
            ST_AsGEOJSON
            ST_AsLatLonText
            ST_AsText
            ST_X
            ST_Y
        """
        return cls._connected(
            "SELECT ST_X(%s), ST_Y(%s)", (hash, hash, )
        )

