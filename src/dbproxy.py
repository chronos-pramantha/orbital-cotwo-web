# coding=utf-8
"""
Proxy class for all connections
"""
import psycopg2
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select, create_engine

__author__ = 'Lorenzo'

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
    print('ENGINE STARTED on DB: {}\n'.format(db))
    return db, create_engine(
        'postgresql://{}:{}@localhost/{}'.format(
            USER, PWD, db
        ),
        echo=echo
    )

DB, ENGINE = start_postgre_engine()


class dbProxy:
    """
    Handle context variable for database access.

    Database Manipulation Layer Wrapper. Wraps Access/Data Layer.

    It let perform the query in two ways:
    - using the psycopg2 driver's cursor with the `_connected()` and
     `connection()` methods
    - using SQLAlchemy by creating a session with `create_session()` if high-level
     ORM functions or transactions are needed or directly using `alchemy.execute(query)`.
    These methods can guarantee a quite flexible use fo the database.
    """
    alchemy = ENGINE.connect()

    @classmethod
    def __connection(cls):
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
        conn = cls.__connection()
        cur = conn.cursor()
        query = cur.mogrify(
            query,
            kwargs['values']
        ) if kwargs.get('values') else cur.execute(query)
        cur.execute(query)
        result = cur.fetchone() if not kwargs.get('multi') else cur.fetchall()
        cur.close()
        conn.close()
        return result

    @classmethod
    def create_session(cls, db='gis', engine=None):
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
            engine = start_postgre_engine(db, False)
            Session = sessionmaker()
            Session.configure(bind=engine)
            session = Session()
        return session

    @classmethod
    def create_tables_in_databases(cls, base):
        """Create a Schema to store CO2 data in the official and test databases"""
        for db in DATABASES:
            engine = start_postgre_engine(db)
            base.metadata.create_all(
                engine[1],
                checkfirst=True
            )
            with psycopg2.connect('postgresql://{}:{}@localhost/{}'.format(
                    USER, PWD, db
                )
            ) as conn:
                conn.cursor().execute('UPDATE t_areas SET aoi = ST_SnapToGrid(aoi, 1.4);')

    @classmethod
    def get_by_id(cls, row_id,  table=None):
        """
        Get a row by id.

        :param row_id: an id from a row
        :param object table: the mapper object of a table
        :return tuple:
        """
        from src.xco2 import Xco2
        if not table:
            table = Xco2
        name = table.__tablename__
        return cls._connected(
            'SELECT * FROM ' + name + ' WHERE id = %s;',
            **{
                'values': (row_id, ),
                'multi': None
            }
        )
