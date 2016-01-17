# coding=utf-8
"""
Test queries over the t_xco2 table
"""
import unittest
from random import randint
from sqlalchemy import select, func

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
        # insert some rows
        util_populate_table(self.dataset, self.test_length, self.session)
        # pick a random sample
        self.i = randint(0, 9)
        self.lat, self.long = self.dataset['latitude'][self.i], self.dataset['longitude'][self.i]

    def test_query_point_in_db(self):
        """Store and retrieve a point using Geometry and Geography"""
        print('##### TEST1 #####')
        #print(lat, long)

        r = dbOps.single_point_query(self.long, self.lat)
        # print(query)
        #print(str(type(r)))
        try:
            self.assertAlmostEqual(
                r.xco2,
                self.dataset['xco2'][self.i],
                delta=0.001
            )
            print('PASSED')
        except AssertionError as e:
            print('FAILED')
            raise e

    def test_unshape_geo_hash(self):
        """Test unshaping from PostGIS objects to EWKT"""
        print('##### TEST2 #####')
        r = dbOps.single_point_query(self.long, self.lat)
        #print(r.coordinates, r.pixels)
        st1 = spatialRef.unshape_geo_hash(str(r.coordinates))
        st2 = spatialRef.unshape_geo_hash(str(r.pixels))
        try:
            self.assertEqual(st1, st2)
            print('PASSED')
        except AssertionError:
            print('FAILED')
            raise e

    def test_get_by_id(self):
        """Test get_by_id"""
        print('##### TEST3 #####')
        r = dbOps.single_point_query(self.long, self.lat)
        r = dbOps.get_by_id(r.id)
        # print(r)
        st1 = spatialRef.unshape_geo_hash(r[3])
        #print(st1)
        try:
            self.assertAlmostEqual(st1[0], self.long, delta=0.001)
            self.assertAlmostEqual(st1[1], self.lat, delta=0.001)
            print('PASSED')
        except AssertionError as e:
            print('FAILED')
            raise e

    def test_ST_AsGEOJSON(self):
        """Test querying one point as a GEOJSON object"""
        print('##### TEST4 #####')
        import json
        table = Xco2
        id_ = dbOps.single_point_query(self.long, self.lat).id
        query = select(
            [table.id, func.ST_AsGEOJSON(table.coordinates)]
        ).where(Xco2.id == id_)
        result = spatialRef.exec_func_query(query)
        # the query asked for a JSON
        result = json.loads(result[1])
        try:
            self.assertAlmostEqual(result['coordinates'][0], self.long, delta=0.0001)
            self.assertAlmostEqual(result['coordinates'][1], self.lat, delta=0.0001)
            print('PASSED')
        except AssertionError as e:
            print('FAILED')
            raise e


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
