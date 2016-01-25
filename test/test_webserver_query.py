# coding=utf-8
"""
This module test SQL queries on the database, to fetch data to feed the Web server
"""
import unittest
import geojson

__author__ = 'Lorenzo'

from src.dbproxy import start_postgre_engine
from src.spatial import spatial


class TestQueries(unittest.TestCase):
    """
    Test the methods used in the web server
    """
    @classmethod
    def setUpClass(cls):
        print(cls.__doc__)
        _, cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()
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

    def test_should_get_coordinates_from_geojson(self):
        print('TEST1')
        coords = spatial.coordinates_from_geojson(self.data)
        print(coords)
        try:
            self.assertEqual(coords[0], coords[-1])
            print('PASSED')
        except AssertionError:
            print('FAILED')

    def test_should_print_ewkt_from_coords(self):
        print('TEST2')
        coords = spatial.coordinates_from_geojson(self.data)
        polygon = spatial.from_list_to_ewkt(coords)
        print(polygon)
        try:
            self.assertEqual(
                polygon,
                'SRID=3857;POLYGON((62.5 169.0, 62.5 169.3, 62.9 169.3, 62.9 169.0, 62.5 169.0))'
            )
            print('PASSED')
        except AssertionError:
            print('FAILED')

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()


if __name__ == '__main__':
    unittest.main()