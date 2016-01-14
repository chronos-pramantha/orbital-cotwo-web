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

from sqlalchemy import create_engine
from sqlalchemy import orm
from sqlalchemy import Table, Column, Integer, Float, MetaData, DateTime
from sqlalchemy import UniqueConstraint
from geoalchemy2 import Geography, Geometry
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
DATABASES = ('gis', 'test', )  # two databases are created, one official and one test


class Xco2(Base):
    __tablename__ = 't_co2'

    id = Column('id', Integer, primary_key=True)
    xco2 = Column('xco2', Float)
    timestamp = Column('timestamp', DateTime)
    # use a geography with coordinates
    coordinates = Column('coordinates', Geography('POINT', srid=4326, spatial_index=True))
    # use a geometry with pixels (for Web maps)
    pixels = Column('pixels', Geometry('POINT', srid=3857, spatial_index=True))

    __table_args__ = (
        UniqueConstraint('timestamp', 'coordinates', name='uix_time_coords'),
    )

    def __init__(self, xco2, timestamp, latitude, longitude):
        self.xco2 = xco2
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    """@orm.reconstructor
    def init_on_load(self):
        self.xco2 = self.xco2
        self.timestamp = self.timestamp
        self.latitude = self._lat_long[0]
        self.longitude = self._lat_long[1]"""

    def __repr__(self):
        return 'Point {coordinates!r}'.format(
            coordinates=self._lat_long
        )

    def __str__(self):
        return 'Point {coordinates!s} has Xco2 level at {xco2!s}'.format(
            coordinates=self._lat_long,
            xco2=self.xco2
        )

    @classmethod
    def shape_geometry(cls, lat, long):
        """Return a EWKT string representing a point, to be passed to
        `ST_GeomFromEWKT` PostGIS function"""
        return 'SRID=3857;POINT({} {})'.format(
            lat,
            long
        )

    @classmethod
    def shape_geography(cls, lat, long):
        """Return a EWKT string representing a point, to be passed to
        `ST_GeogFromText` PostGIS function"""
        return 'SRID=4326;POINT({} {})'.format(
            lat,
            long
        )

    # #todo: implement descriptors ?
    @property
    def _lat_long(self):
        """Return latitude and longitude"""
        if hasattr(self, 'latitude') and hasattr(self, 'longitude'):
            return self.latitude, self.longitude
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')

    @property
    def _coordinates(self):
        if hasattr(self, 'latitude') and hasattr(self, 'longitude'):
            return self.shape_geography(self.latitude, self.longitude)
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')

    @property
    def _pixels(self):
        if hasattr(self, 'latitude') and hasattr(self, 'longitude'):
            return self.shape_geometry(self.latitude, self.longitude)
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')


def start_postgre_engine(db=None, echo=True):
    """
    Return SQLAlchemy engine.

    :param str db: name of the database
    :param bool echo: print logging if True
    :return: an instance of sqlalchemy.engine
    """
    user = 'gis'
    pwd = 'gis'
    db = db if db in DATABASES else 'test'
    return create_engine(
        'postgresql://{}:{}@localhost/{}'.format(
            user, pwd, db
        ),
        echo=echo
    )


def create_tables_in_databases():
    """Create a Schema to store CO2 data in the official and test databases"""

    [Base.metadata.create_all(
        start_postgre_engine(db),
        checkfirst=True
    ) for db in DATABASES]


if __name__ == '__main__':
    create_tables_in_databases()
