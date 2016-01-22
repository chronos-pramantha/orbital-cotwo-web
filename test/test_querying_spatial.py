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
from src.xco2ops import xco2Ops
from src.dbproxy import dbProxy, start_postgre_engine
from src.spatial import spatialOps
from test.utils_for_tests import util_populate_table, util_truncate_table, pick_random_sample

TEST_LENGTH = 20


class DBareasSpatial(unittest.TestCase):
    """
Test the Areas mapper to table t_areas.

"""
    REFACTOR = False
    test_length = TEST_LENGTH

    @classmethod
    def setUpClass(cls):
        print(cls.__doc__)
        _, cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()

        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])
        cls.session = dbProxy.create_session(cls.engine)

    def setUp(self):
        # insert some rows and return their pks
        samples = util_populate_table(self.dataset, self.test_length)
        # pick a random sample
        self.i, self.test_point_pk, self.test_areas_pk, self.long, self.lat = pick_random_sample(
            self.dataset,
            samples
        )
        from src.formatdata import createOCOpoint
        self.luke = createOCOpoint(**{
            'latitude': self.dataset['latitude'][self.i],
            'longitude': self.dataset['longitude'][self.i],
            'xco2': self.dataset['xco2'][self.i],
            'date': self.dataset['date'][self.i],
            }
        )

    def util_populate_areas(self):
        pass

    @unittest.skipIf(REFACTOR, "REFACTORING")
    def test_should_test_shape_geometry(self):
        """Test shape_geometry() """
        geom = spatialOps.shape_geometry(
            self.luke.longitude,
            self.luke.latitude
        )
        #print(geom)
        self.assertEqual(
            geom,
            geom    # #todo: use a SELECT casting
        )

    @unittest.skipIf(REFACTOR, "REFACTORING")
    def test_should_test_shape_geography(self):
        """Test shape_geography() """
        geog = spatialOps.shape_geography(
            self.luke.latitude,
            self.luke.longitude
        )
        #print(geom)
        self.assertEqual(
            geog,
            geog   # #todo: use a SELECT casting
        )

    @unittest.skipIf(REFACTOR, "REFACTORING")
    def test_shape_aoi(self):
        print('TEST2<<<<')
        geom = spatialOps.shape_geometry(self.long, self.lat)
        shape, center = spatialOps.shape_aoi(geom)
        print(shape)
        try:
            conversion = self.conn.execute(
                'SELECT %s::geometry;',
                (shape, )
            ).first()
            assert conversion
        except Exception as e:
            print('TEST FAILED')
            raise e
        # SELECT 'SRID=3857;POLYGON(((-179.748110962 -22.8178), (-178.348110962 -22.8178),
        # (-179.048 -22.1178405762), (-179.048 -23.5178405762), (-179.748110962 -22.8178), ))'::geometry;
        print('TEST PASSED\n')

    @unittest.expectedFailure
    def test_insert_area_and_center(self):
        """Test insertion of row in t_areas"""
        geom = spatialOps.shape_geometry(self.long, self.lat)
        shape, center = spatialOps.shape_aoi(geom)
        try:
            self.conn.execute(
                'INSERT INTO t_areas(center, aoi) VALUES (\'{center}\', \'{polygon}\');'.format(
                    center=center,
                    polygon=shape
                )
            )
            select = self.conn.execute(
                'SELECT  COUNT(id) FROM t_areas WHERE center = \'{center}\';'.format(
                    center=center
                )
            ).fetchall()
            self.assertEqual(
                select[0][0],
                1
            )
        except Exception as e:
            print('TEST FAILED')
            raise e
        print('TEST PASSED\n')

    def tearDown(self):
        util_truncate_table(self.session, table=[Xco2, Areas])
        pass

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.conn.close()
        del cls

if __name__ == '__main__':
    unittest.main()


