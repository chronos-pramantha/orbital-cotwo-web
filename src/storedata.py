# coding=utf-8
"""
Binding to persistence layer (SQLite for test, PostGRE for production)
"""
import sqlite3

__author__ = 'Lorenzo'

from config import _PATH
from src.formatdata import OCOpoint
from config import t_name


def format_namedtuple(func, *args):
    """Format namedtuple values into SQL-compliant"""
    def wrapper(*args):
        if isinstance(args[0], OCOpoint):
            obj = args[0]
            values = tuple([
                getattr(obj, f)
                if f != 'timestamp'
                else getattr(obj, f).strftime('%Y-%m-%d %H:%M:%S.%f')
                for f in obj._fields
            ])
            return func(values)
        else:
            raise TypeError('Input has to be of type \'OCOpoint\'')
    return wrapper


@format_namedtuple
def namedtuple_values_to_sql(values):
    """Take a OCO2point and store it in the database"""
    return (
        'INSERT INTO {name!s} {fields!s} VALUES {values!s}'.format(
            name=t_name,
            fields=('timestamp', 'xco2', 'latitude', 'longitude'),
            values=values
        )
    )


def go_execute(sql):
    result = None
    with sqlite3.connect(_PATH) as conn:
        c = conn.cursor()
        print('Executing: ', sql)
        c.execute(sql)
        result = c
        conn.commit()
    return result
