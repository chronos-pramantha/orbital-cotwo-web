# coding=utf-8
import os
import sqlite3
from datetime import datetime

__author__ = 'Lorenzo'

from src.formatdata import OCOpoint

sqlite_file = 'oco2_test.sqlite'    # name of the sqlite database file
t_name = 'table_xco2'  # name of the table to be created
fields = tuple([f for f in OCOpoint._fields])

_PATH = os.path.join(os.getcwd(), sqlite_file)

CREATE = (
    'CREATE TABLE IF NOT EXISTS '
    '{t_name!s} (t_key INTEGER PRIMARY KEY, '
    'latitude REAL NOT NULL, longitude REAL NOT NULL, '
    'xco2 REAL NOT NULL, timestamp DATETIME) '
).format(t_name=t_name)

CREATE_INDEX = (
    'CREATE UNIQUE INDEX IF NOT EXISTS idx__lat_long ON '
    '{t_name!s} (latitude, longitude)'
).format(t_name=t_name)

# Moved to next implementation (insert timestamp in index)
# CREATE_INDEX = (
#    'CREATE UNIQUE INDEX IF NOT EXISTS datetime_lat_long ON '
#    '{t_name!s} (timestamp, latitude, longitude)'
# ).format(t_name=t_name)


def field_type(field):
    return {
        'timestamp': datetime.datetime
    }.get(field, float)


def create_db():
    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Creating a new SQLite table with 1 column
    c.execute(CREATE)
    c.execute(CREATE_INDEX)

    # Committing changes and closing the connection to the database file
    conn.commit()

    conn.close()

if __name__ == '__main__':
    create_db()