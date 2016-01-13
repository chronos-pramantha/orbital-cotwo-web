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

    def __repr__(self):
        return 'Point {coordinates!r}'.format(
            coordinates=repr(self.coordinates)
        )

    def __str__(self):
        return 'Point {coordinates!s} has Xco2 level at {xco2!s}'.format(
            coordinates=repr(self.coordinates),
            xco2=str(self.xco2)
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
