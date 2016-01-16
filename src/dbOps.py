# coding=utf-8
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, select

__author__ = 'Lorenzo'

from src.xco2 import Xco2
from config.config import DATABASES, USER, PWD


def start_postgre_engine(db=None, echo=True):
    """
    Return SQLAlchemy engine.

    :param str db: name of the database (databases names in config.config.DATABASES)
    :param bool echo: print logging if True
    :return: an instance of sqlalchemy.engine
    """
    db = db if db in DATABASES else 'test'
    return db, create_engine(
        'postgresql://{}:{}@localhost/{}'.format(
            USER, PWD, db
        ),
        echo=echo
    )

DB, ENGINE = start_postgre_engine()


class dbOps:
    connection = ENGINE.connect()

    @classmethod
    def create_tables_in_databases(cls, base):
        """Create a Schema to store CO2 data in the official and test databases"""

        [base.metadata.create_all(
            start_postgre_engine(db)[1],
            checkfirst=True
        ) for db in DATABASES]

    @classmethod
    def create_session(cls, engine=None):
        """
        Start a session.

        :param engine:
        :return:
        """
        # if a engine in passed used it, else use the one
        # at the top of the this module
        engine = engine if engine else ENGINE
        if engine:
            Session = sessionmaker()
            Session.configure(bind=engine)
            session = Session()
        else:
            # fallback: create a new engine
            engine = start_postgre_engine('test', False)
            Session = sessionmaker()
            Session.configure(bind=engine)
            session = Session()
        return session

    @classmethod
    def store_xco2(cls, xobject):
        """Store a Xco2 relevation"""
        ins = Xco2.__table__.insert().values(
            xco2=xobject.xco2,
            timestamp=xobject.timestamp,
            coordinates=xobject.shape_geography(
                xobject.latitude,  xobject.longitude),
            pixels=Xco2.shape_geometry(
                xobject.latitude, xobject.longitude)
        )
        result = cls.connection.execute(ins)
        return result.inserted_primary_key

    @classmethod
    def bulk_dump(cls, objs_generator):
        """
        Dump in the database big amounts of objects from a generator.

        :param iter objs_generator:
        """
        while True:
            try:
                obj = next(objs_generator)
                new = Xco2(
                    xco2=obj.xco2,
                    timestamp=obj.timestamp,
                    latitude=obj.latitude,
                    longitude=obj.longitude
                )
                cls.store_xco2(new)
            except StopIteration:
                return
            except Exception as e:
                raise e


    @classmethod
    def build_single_point_query(cls, lat, long, mode='geometry'):
        """
        Build a query on Geometry or Geography field.

        :param float lat: latitude
        :param float long: longitude
        :param str mode: geometry or geography
        :return ResultProxy: query results
        """
        func = 'shape_' + mode if mode in ('geometry', 'geography',) else None
        if func:
            fltr = getattr(Xco2, func)(lat, long)
            print(fltr)
            query = select([Xco2]).where(
                Xco2.coordinates == fltr
            )
        else:
            raise ValueError('mode can be only geometry or geography')
        return query