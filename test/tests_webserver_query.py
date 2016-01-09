# coding=utf-8
"""
This module test SQL queries on the database, to fetch data to feed the Web server
"""
import unittest
import sqlite3
import geojson

__author__ = 'Lorenzo'

from config.config import _PATH
test_db = _PATH


class TestQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create a connection
        cls.conn = sqlite3.connect(test_db)
        cls.data = geojson.dumps(
            {
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [62.5, 169.0],
                            [62.5, 169.3],
                            [62.9, 169.3],
                            [62.9, 169.0],
                            [62.5, 169.0]
                        ]
                    ]
                }
            })

    def test_should_select_test_data_fake(self):
        # ((nw_lat, nw_long), (se_lat, sw_long), )
        from src.webserver.utils import get_coordinates_from_geojson
        coords = [g for g in list(get_coordinates_from_geojson(self.data))[:3]]
        print(coords)
        coords = (coords[0], coords[2], )
        from src.webserver.utils import build_a_select

        from src.storedata import go_execute
        results = go_execute(build_a_select(coords))
        for r in results:
            print(r)


    @classmethod
    def tearDownClass(cls):
        cls.conn.close()


if __name__ == '__main__':
    unittest.main()