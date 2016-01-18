# coding=utf-8
"""
Test queries over the t_areas table and others with geospatial functions
"""
import unittest
from random import randint
from sqlalchemy import select, func

__author__ = 'Lorenzo'

from files.loadfiles import return_files_paths, return_dataset

from src.xco2 import Xco2, Areas
from src.dbops import dbOps, start_postgre_engine
from src.spatial import spatialRef
from test.tests_storedata import util_populate_table, util_truncate_table

TEST_LENGTH = 20


class DBareasSpatial(unittest.TestCase):
    REFACTOR = True
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
        self.util_populate_areas()
        # pick a random sample
        self.i = randint(0, 9)
        self.lat, self.long = self.dataset['latitude'][self.i], self.dataset['longitude'][self.i]

    def util_populate_areas(self):
        pass

    #@unittest.skipIf(REFACTOR, "REFACTORING")
    def test_write_area(self):
        """Store a AoI from a point"""
        print('TEST1<<<<')
        new = Areas(self.long, self.lat)
        print(str(new))

    #@unittest.skipIf(REFACTOR, "REFACTORING")
    def test_shape_aoi(self):
        print('TEST2<<<<')
        result = spatialRef.shape_aoi((self.long, self.lat))
        print(result)

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


