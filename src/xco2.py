# coding=utf-8
"""
Create database table and bind to persistence layer (PostGRE/PostGIS)
<https://www.python.org/dev/peps/pep-0249/>
"""

__author__ = 'Lorenzo'

#
# Before running this script INSTALL and CREATE THE DATABASES (gis and test)
# as explained in WIKI.md
#

from sqlalchemy import orm
from sqlalchemy import Table, Column, Integer, Float, MetaData, DateTime
from sqlalchemy import UniqueConstraint
from geoalchemy2 import Geography, Geometry
from sqlalchemy.ext.declarative import declarative_base

from config.config import DATABASES


Base = declarative_base()


class Xco2(Base):
    """
    Main table's model
    """
    #
    # Table definition
    # ------------------------------------------------------------------------
    __tablename__ = 't_co2'

    id = Column('id', Integer, primary_key=True)
    xco2 = Column('xco2', Float, nullable=False)
    timestamp = Column('timestamp', DateTime, nullable=False)
    # use a geography with coordinates
    coordinates = Column(
        'coordinates',
        Geography('POINT', srid=4326, spatial_index=True),
        nullable=False
    )
    # use a geometry with pixels (for Web maps)
    pixels = Column(
        'pixels',
        Geometry('POINT', srid=3857, spatial_index=True),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint('timestamp', 'coordinates', name='uix_time_coords'),
    )

    #
    # Constructor
    # ------------------------------------------------------------------------
    def __init__(self, xco2, timestamp, longitude, latitude):
        self.xco2 = xco2
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    # #todo: implement the reconstructor (from query object to py object)
    @orm.reconstructor
    def init_on_load(self):
        from src.spatial import spatialRef
        self.latitude = spatialRef.unshape_geo_hash(str(self.coordinates))[1]
        self.longitude = spatialRef.unshape_geo_hash(str(self.coordinates))[0]

    def __repr__(self):
        return 'Point {coordinates!r}'.format(
            coordinates=self._long_lat
        )

    def __str__(self):
        return 'Point {coordinates!s} has Xco2 level at {xco2!s}'.format(
            coordinates=self._long_lat,
            xco2=self.xco2
        )

    @classmethod
    def shape_geometry(cls, long, lat):
        """Return a EWKT string representing a point, to be passed to
        `ST_GeomFromEWKT` PostGIS function"""
        return 'SRID=3857;POINT({} {})'.format(
            long,
            lat
        )

    @classmethod
    def shape_geography(cls, long, lat):
        """Return a EWKT string representing a point, to be passed to
        `ST_GeogFromText` PostGIS function"""
        return 'SRID=4326;POINT({} {})'.format(
            long,
            lat
        )

    # #todo: implement descriptors ?
    @property
    def _long_lat(self):
        """Return latitude and longitude"""
        if all(k in self.__dict__.keys() for k in ('latitude', 'longitude',)):
            return self.longitude, self.latitude
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')

    @property
    def hash_coordinates(self):
        if all(k in self.__dict__.keys() for k in ('latitude', 'longitude',)):
            return self.shape_geography(self.longitude, self.latitude)
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')

    @property
    def hash_pixels(self):
        if all(k in self.__dict__.keys() for k in ('latitude', 'longitude',)):
            return self.shape_geometry(self.longitude, self.latitude)
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')


if __name__ == '__main__':
    try:
        from src.dbops import dbOps
        dbOps.create_tables_in_databases(Base)
        print('####################################\n'
              '#Databases and tables created      #\n'
              '#Enter your psql command line and  #\n'
              '#check that databases {} #\n'
              '#and table t_co2 are present.      #\n'
              '####################################\n'.format(DATABASES))
    except Exception as e:
        raise e
