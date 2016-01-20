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
from test.tests_storedata import util_populate_table, util_truncate_table

TEST_LENGTH = 20


class DBareasSpatial(unittest.TestCase):
    """
Test the Areas mapper to table t_areas.

"""
    REFACTOR = True
    test_length = TEST_LENGTH

    @classmethod
    def setUpClass(cls):
        print(cls.__doc__)
        _, cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()

        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])
        cls.session = dbProxy.create_session(cls.engine)
        # populate t_co2 with some data
        util_populate_table(cls.dataset, cls.test_length)

    def setUp(self):
        self.util_populate_areas()
        # pick a random sample
        self.i = i = randint(0, 9)
        self.lat, self.long = self.dataset['latitude'][i], self.dataset['longitude'][i]
        from src.formatdata import createOCOpoint
        self.luke = createOCOpoint(**{
            'latitude': self.dataset['latitude'][i],
            'longitude': self.dataset['longitude'][i],
            'xco2': self.dataset['xco2'][i],
            'date': self.dataset['date'][i],
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
    def test_write_area(self):
        """Test object creation for Areas"""
        print('TEST1<<<<')
        new = Areas(self.long, self.lat)
        print(str(new))
        print('TEST PASSED\n')

    #@unittest.skipIf(REFACTOR, "REFACTORING")
    def test_shape_aoi(self):
        print('TEST2<<<<')
        shape, center = spatialOps.shape_aoi((self.long, self.lat))
        print(shape)
        try:
            conversion = self.conn.execute(
                'SELECT \'' + shape + '\'::geometry;'
            ).fetchall()
        except Exception as e:
            print('TEST FAILED')
            raise e
        # SELECT 'SRID=3857;POLYGON(((-179.748110962 -22.8178), (-178.348110962 -22.8178),
        # (-179.048 -22.1178405762), (-179.048 -23.5178405762), (-179.748110962 -22.8178), ))'::geometry;
        print('TEST PASSED\n')

    @unittest.skipIf(REFACTOR, "REFACTORING")
    def test_insert_area_and_center(self):
        """Test insertion of row in t_areas"""
        shape, center = spatialOps.shape_aoi((self.long, self.lat))
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
        util_truncate_table(self.session, table=[Areas])
        pass

    @classmethod
    def tearDownClass(cls):
        util_truncate_table(cls.session, table=[Xco2])
        cls.session.close()
        cls.conn.close()
        del cls

if __name__ == '__main__':
    unittest.main()


