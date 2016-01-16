# coding=utf-8
"""
Test queries over the t_xco2 table
"""
import unittest

__author__ = 'Lorenzo'

from src.xco2 import Xco2, start_postgre_engine
from test.tests_storedata.DBTest import util_create_session

class TestQuerying(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()

    def setUp(self):
        pass

    def test_if_point_in_db(self):



    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        del cls

if __name__ == '__main__':
    unittest.main()
