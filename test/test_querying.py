# coding=utf-8
"""
Test queries over the t_xco2 table
"""
import unittest
from sqlalchemy import select, func

__author__ = 'Lorenzo'

from files.loadfiles import return_files_paths, return_dataset

from src.xco2 import Xco2, Areas
from src.dbproxy import dbProxy, start_postgre_engine
from src.spatial import spatial
from test.utils_for_tests import util_populate_table, util_truncate_table, pick_random_sample


class TestQuerying(unittest.TestCase):
    """
Test querying the Xco2 mapper and the t_co2 table.

"""
    TEST_LENGTH = 20
    REFACTOR = False

    @classmethod
    def setUpClass(cls):
        print(cls.__doc__)
        _, cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()
        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])

    def setUp(self):
        self.test_length = self.TEST_LENGTH
        self.session = dbProxy.create_session(self.engine)
        # insert some rows and return their pks
        samples = util_populate_table(self.dataset, self.test_length)
        # pick a random sample
        self.i, self.test_point_pk, self.test_areas_pk, self.long, self.lat = pick_random_sample(
            self.dataset,
            samples
        )

    """@unittest.skipIf(REFACTOR, 'Refactoring')
    def test_query_point_in_db(self):

        print('##### TEST1 #####')
        # find a point using geometry
        geom = spatialOps.shape_geometry(self.long, self.lat)
        r1 = select([Xco2.xco2]).where(Xco2.geometry == geom)
        r1 = self.conn.execute(r1).first()
        # find a point using primary key
        r2 = select([Xco2.xco2]).where(Xco2.id == self.test_point_pk)
        r2 = self.conn.execute(r2).first()
        # test if record is the same
        try:
            self.assertAlmostEqual(
                r1[0],
                r2[0],
                delta=0.00001
            )
            print('PASSED')
        except AssertionError as e:
            print('FAILED')
            raise e"""

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_unshape_geo_hash(self):
        """Test unshaping from PostGIS objects to EWKT"""
        print('##### TEST2 #####')
        r1 = select([Xco2]).where(Xco2.id == self.test_point_pk)
        r = self.conn.execute(r1).first()
        try:
            spatial.unshape_geo_hash(r[3])
            print('PASSED')
        except Exception as e:
            print('FAILED')
            raise e

    """@unittest.skipIf(REFACTOR, 'Refactoring')
    def test_get_by_id(self):
        print('##### TEST3 #####')
        r = dbProxy.get_by_id(self.test_point_pk)
        # print(r)
        st1 = spatialOps.unshape_geo_hash(r[3])
        #print(st1)
        try:
            self.assertAlmostEqual(st1[0], self.long, delta=0.001)
            self.assertAlmostEqual(st1[1], self.lat, delta=0.001)
            print('PASSED')
        except AssertionError as e:
            print('FAILED')
            raise e"""

    """@unittest.skipIf(REFACTOR, 'Refactoring')
    def test_ST_AsGEOJSON(self):
        print('##### TEST4 #####')
        import json
        table = Xco2
        # get a random row
        r1 = select([Xco2]).where(Xco2.id == self.test_point_pk)
        id_ = self.conn.execute(r1).first()[0]
        # build a query
        query = select(
            [table.id, func.ST_AsGEOJSON(table.geometry)]
        ).where(table.id == id_)
        # print a compiled statement
        #print(str(query.compile()))
        # execute query
        result = spatialOps.exec_func_query(query)
        # the query asked for a JSON
        result = json.loads(result[1])
        try:
            #print(str(type(result['coordinates'][0])), result['coordinates'][0])
            #print(str(type(self.long)), float(self.long))
            self.assertAlmostEqual(result['coordinates'][0], self.long, delta=0.001)
            self.assertAlmostEqual(result['coordinates'][1], self.lat, delta=0.001)
            print('PASSED')
        except AssertionError as e:
            print('FAILED')
            raise e"""


    def tearDown(self):
        util_truncate_table(self.session, [Xco2, Areas])
        del self.session
        pass

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        del cls

if __name__ == '__main__':
    unittest.main()
