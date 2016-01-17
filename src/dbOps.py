# coding=utf-8
import psycopg2
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select, create_engine

__author__ = 'Lorenzo'

from src.xco2 import Xco2
from config.config import DATABASES, USER, PWD


def start_postgre_engine(db=None, echo=False):
    """
    Return SQLAlchemy engine.

    :param str db: name of the database (databases names in config.config.DATABASES)
    :param bool echo: print logging if True
    :return: an instance of sqlalchemy.engine
    """
    from config.config import TEST
    # use the db in the argument or check the TEST variable
    db = db if db and db in DATABASES else {True: 'test', False: 'gis'}.get(TEST)
    return db, create_engine(
        'postgresql://{}:{}@localhost/{}'.format(
            USER, PWD, db
        ),
        echo=echo
    )

DB, ENGINE = start_postgre_engine()   # set the db here


class dbProxy:
    """
    Handle context variable for datbase access
    """
    alchemy = ENGINE.connect()

    @classmethod
    def connection(cls):
        """Connect to the PostgreSQL database.  Returns a database connection."""
        return psycopg2.connect('postgresql://{}:{}@localhost/{}'.format(
                USER, PWD, DB
            )
        )

    @classmethod
    def _connected(cls, query, **kwargs):
        """
        Wrap execute() function to open and close properly connection and cursor.
        Use psycopg2 as driver.
        """
        conn = cls.connection()
        cur = conn.cursor()
        cur.execute(
            query,
            kwargs['values']
        ) if kwargs.get('values') else cur.execute(query)
        result = cur.fetchone() if not kwargs.get('multi') else cur.fetchall()
        cur.close()
        conn.close()
        return result

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


class dbOps(dbProxy):
    """
    Handle functions for non-spatial read/write operation on the db.
    """
    @classmethod
    def create_tables_in_databases(cls, base):
        """Create a Schema to store CO2 data in the official and test databases"""

        [base.metadata.create_all(
            start_postgre_engine(db)[1],
            checkfirst=True
        ) for db in DATABASES]

    @classmethod
    def get_by_id(cls, id):
        """
        Get a row by id.

        :param id: an id from a row
        :return tuple:
        """
        return cls._connected(
            "SELECT * FROM t_co2 WHERE id = %s;",
            **{'values': (id, ), 'multi': None}
        )

    @classmethod
    def store_xco2(cls, xobject):
        """Store a Xco2 relevation"""
        ins = Xco2.__table__.insert().values(
            xco2=xobject.xco2,
            timestamp=xobject.timestamp,
            coordinates=xobject.shape_geography(
                xobject.longitude, xobject.latitude),
            pixels=Xco2.shape_geometry(
                xobject.longitude, xobject.latitude)
        )
        result = cls.alchemy.execute(ins)
        return result.inserted_primary_key

    @classmethod
    def bulk_dump(cls, objs_generator):
        """
        Dump in the database big amounts of objects from a generator.

        # #todo: refactor using session and add_all()

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
    def single_point_query(cls, long, lat, mode='geometry'):
        """
        Build a query on Geometry or Geography field.

        :param float lat: latitude
        :param float long: longitude
        :param str mode: geometry or geography
        :return Query: query object
        """
        func = 'shape_' + mode if mode in ('geometry', 'geography',) else None
        if func:
            fltr = getattr(Xco2, func)(long, lat)
            query = select([Xco2]).where(
                Xco2.coordinates == fltr
            )
            result = cls.alchemy.execute(query).fetchone()
        else:
            raise ValueError('mode can be only geometry or geography')
        return result