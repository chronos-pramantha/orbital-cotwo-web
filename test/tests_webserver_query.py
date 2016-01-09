# coding=utf-8
"""
This module test SQL queries on the database, to fetch data to feed the Web server
"""
import unittest
import sqlite3

__author__ = 'Lorenzo'

from config.config import _PATH
test_db = _PATH


class TestQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create a connection
        cls.conn = sqlite3.connect(test_db)

    def test_should_select_test_data(self):
        coords = ((62.5, 169.3), (62.9, 169.0), )
        def run_a_select(coords):
            # just a placeholder query, works only with coordinates in the
            # north-eastern quarter
            return (
                'SELECT latitude,longitude, xco2 from table_xco2 WHERE'
                '((latitude > %s and latitude < %s) and (longitude > %s and longitude < %s))'
            ).fomat(coords[0][0], coords[1][0], coords[1][1], coords[0][1])


        from src.storedata import go_execute

        go_execute(run_a_select(coords))


    @classmethod
    def tearDownClass(cls):
        cls.conn.close()


if __name__ == '__main__':
    unittest.main()