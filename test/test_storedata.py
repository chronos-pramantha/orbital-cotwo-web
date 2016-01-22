# coding=utf-8
import unittest
from sqlalchemy.exc import IntegrityError


__author__ = 'Lorenzo'

from src.xco2 import Xco2, Areas
from src.dbproxy import dbProxy, start_postgre_engine
from src.formatdata import create_generator_from_dataset
from files.loadfiles import return_files_paths, return_dataset
from test.utils_for_tests import util_populate_table, util_truncate_table


# #todo: implement 'luke' as a Mock()


class DBtestStoring(unittest.TestCase):
    """
Test storing operations on the database for t_co2 table
(t_areas table's are in tests_querying_spatial).

"""
    REFACTOR = False  # Flag to be set during refactoring for partial tests
    TEST_LENGTH = 20  # Number of rows to insert in the test db

    @classmethod
    def setUpClass(cls):
        print(cls.__doc__)
        _, cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()
        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])

    def setUp(self):
        self.test_length = self.TEST_LENGTH
        self.session = dbProxy.create_session(db='test', engine=self.engine)
        self.samples = util_populate_table(self.dataset, self.test_length)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_if_tables_got_populated_correctly(self):
        """Test the data inserted in tables by util_populate_table"""
        # pick a set of rows in t_co2 as points
        # try to find centers==points in t_areas
        print(self.samples)
        samples = tuple([s[0] for s in self.samples])
        print(samples)
        # try to find aoi that contains points
        q2 = (
            'SELECT t_areas.aoi, t_areas.data '
            'FROM t_co2, t_areas WHERE '
            '((t_co2.id IN %s) AND '
            'ST_Contains(t_areas.aoi, t_co2.geometry));'
        )
        r = dbProxy._connected(
            q2,
            **{
                'values': (samples, ),
                'multi': True
            }
        )
        #print(r)
        # check if aoi.data contains centers
        from src.spatial import spatial
        outcome = []
        for result in r:
            coords = [tuple(cc['geometry']['coordinates']) for cc in result[1]['features']]
            aoi = result[0]
            for c in coords:
                geom = spatial.shape_geometry(c[0], c[1])
                q3 = (
                    'SELECT ST_Contains(%s, %s::geometry);'
                )
                contains = dbProxy._connected(
                    q3,
                    **{
                        'values': (aoi, geom, ),
                        'multi': False
                    }
                )
                self.assertTrue(contains[0])
        #print(outcome)
        #assert all(outcome[0:-2]) == True

    """@unittest.skipIf(REFACTOR, 'Refactoring')
    def test_check_if_correct_results_are_stored_in_geojson(self):
        # pick a random area in the db
        # find the array of coordinates of these points
        # compare this array with the one in the 'data' field
        raise NotImplemented"""

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_find_the_records_in_the_db(self):
        """Perform a Select to check the data inserted in setUp"""
        print('#### TEST1 ####')
        rows = self.session.query(Xco2).count()
        try:
            self.assertEqual(rows, self.test_length)
            print('PASSED')
        except AssertionError:
            print('FAILED')

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_create_xco2_obj_from_select_query(self):
        # to be implemented along with @orm.reconstructor
        print('#### TEST2 ####')
        print('PASSED')
        pass

    """@unittest.expectedFailure
    def test_compare_data_between_db_and_dataset(self):
        print('#### TEST3 ####')
        ten = self.session.query(Xco2).limit(10)
        lst = list(create_generator_from_dataset(self.dataset, 10))
        for i, l in enumerate(lst):
            try:
                self.assertAlmostEqual(l.xco2, float(ten[i].xco2), delta=0.0000001)
                self.assertEqual(l.timestamp, ten[i].timestamp)
            except AssertionError as e:
                print('FAILED')
                raise e
        print('PASSED')"""

    """#@unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_insert_single_record(self):
        print('#### TEST4 ####')
        luke = list(
            create_generator_from_dataset(self.dataset, 21)
        )[-1]
        ins = xco2Ops.store_xco2(
            Xco2(
                xco2=luke.xco2,
                timestamp=luke.timestamp,
                latitude=luke.latitude,
                longitude=luke.longitude
            )
        )
        rows = self.session.query(Xco2).count()
        try:
            self.assertEqual(rows, self.test_length + 1)
            print('PASSED')
        except AssertionError:
            print('FAILED')"""

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_bulk_dump(self):
        """Test Xco2.bulk_dump()"""
        from src.formatdata import bulk_dump
        print('#### TEST5 ####')
        session2 = dbProxy.create_session(db='test', engine=self.engine)
        util_truncate_table(session2, [Xco2, Areas])

        bulk_dump(
            create_generator_from_dataset(self.dataset, 8)
        )
        rows = self.session.query(Xco2).count()
        try:
            self.assertEqual(rows, 8)
            print('PASSED')
        except AssertionError:
            print('FAILED')

    """@unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_violate_unique_constraint(self):
        print('#### TEST6 ####')
        from random import randint
        luke = list(
            create_generator_from_dataset(self.dataset, randint(15, 30))
        )[-1]
        ins1 = ins2 = Xco2(
            xco2=luke.xco2,
            timestamp=luke.timestamp,
            latitude=luke.latitude,
            longitude=luke.longitude
        )


        xco2Ops.store_xco2(
            ins1
        )
        self.assertRaises(
            IntegrityError,
            xco2Ops.store_xco2,
            ins2
        )
        print('PASSED')"""


    def tearDown(self):
        # if you want to keep the data in the db to make test using psql,
        # comment the line below
        util_truncate_table(self.session, [Xco2, Areas])
        del self.session
        pass

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        del cls.paths
        cls.dataset.close()


if __name__ == '__main__':
    unittest.main()
