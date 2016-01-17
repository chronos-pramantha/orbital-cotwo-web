# coding=utf-8
"""
Test queries over the t_xco2 table
"""
import unittest
from random import randint

__author__ = 'Lorenzo'

from files.loadfiles import return_files_paths, return_dataset

from src.xco2 import Xco2
from src.dbops import dbOps, start_postgre_engine
from src.spatial import spatialRef
from test.tests_storedata import util_populate_table, util_truncate_table

TEST_LENGTH = 20


class TestQuerying(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()

        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])

    def setUp(self):
        self.test_length = TEST_LENGTH
        self.session = dbOps.create_session(self.engine)
        util_populate_table(self.dataset, self.test_length, self.session)

    def test_query_point_in_db(self):
        """Store and retrieve a point using Geometry and Geography"""
        i = randint(0, 10)
        lat, long = self.dataset['latitude'][i], self.dataset['longitude'][i]
        #print(lat, long)

        query = dbOps.build_single_point_query(long, lat)
        # print(query)
        res = self.conn.execute(query)
        r = res.fetchone()
        # print(r.xco2, self.dataset['xco2'][i])
        try:
            self.assertAlmostEqual(
                r.xco2,
                self.dataset['xco2'][i],
                delta=0.001
            )
            print('PASSED')
        except AssertionError:
            print('FAILED')
        res.close()

    def test_unshape_geo_hash(self):
        i = randint(0, 10)
        lat, long = self.dataset['latitude'][i], self.dataset['longitude'][i]

        query = dbOps.build_single_point_query(long, lat)
        #print(query)
        res = self.conn.execute(query)
        r = res.fetchone()
        #print(r.coordinates, r.pixels)
        st1 = spatialRef.unshape_geo_hash(str(r.coordinates))
        st2 = spatialRef.unshape_geo_hash(str(r.pixels))
        try:
            self.assertEqual(st1, st2)
            print('PASSED')
        except AssertionError:
            print('FAILED')
        res.close()


    def tearDown(self):
        util_truncate_table(self.session)
        del self.session
        pass

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        del cls

if __name__ == '__main__':
    unittest.main()
