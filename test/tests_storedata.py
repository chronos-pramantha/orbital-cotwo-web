# coding=utf-8
import unittest
from sqlalchemy.exc import IntegrityError


__author__ = 'Lorenzo'

from src.xco2 import Xco2
from src.dbops import dbOps, start_postgre_engine
from src.spatial import spatialRef
from files.loadfiles import return_files_paths, return_dataset
from src.formatdata import create_generator_from_dataset


# #todo: implement 'luke' as a Mock()

REFACTOR = False  # Flag to be set during refactoring for partial tests
TEST_LENGTH = 20  # Number of rows to insert in the test db


# ##### UTILITIES FOR TESTS ##################################################
def util_populate_table(dataset, lentest, session):
    """
    Populate the t_co2 table with n rows

    :param numpyArray dataset:
    :param int lentest:
    :param Session session:
    :return:
    """
    # create a generator from the first lentest records in the dataset
    luke = create_generator_from_dataset(dataset, lentest)

    [
        dbOps.store_xco2(
            Xco2(
                xco2=d.xco2,
                timestamp=d.timestamp,
                latitude=d.latitude,
                longitude=d.longitude
            )
        ) for d in luke
    ]


def util_truncate_table(session):
    """Utility to drop table's content"""
    try:
        session.query(Xco2).delete()
        session.commit()
    except:
        session.rollback()
# ##### ############### ######################################################


class DBtest(unittest.TestCase):
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

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_find_the_records_in_the_db(self):
        """Perform a Select to check the data inserted in setUp"""
        rows = self.session.query(Xco2).count()
        try:
            self.assertEqual(rows, self.test_length)
            print('TEST PASSED')
            #print(rows)
        except AssertionError:
            print('TEST FAILED')

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_create_xco2_obj_from_select_query(self):
        # to be implemented along with @orm.reconstructor
        pass

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_compare_data_between_db_and_dataset(self):
        ten = self.session.query(Xco2).limit(10)
        lst = list(create_generator_from_dataset(self.dataset, 10))
        for i, l in enumerate(lst):
            #print(str(type(ten[i].xco2)), ten[i].xco2)
            #print(str(type(l.xco2)), l.xco2)
            try:
                self.assertAlmostEqual(l.xco2, float(ten[i].xco2), delta=0.0000001)
                self.assertEqual(l.timestamp, ten[i].timestamp)
                print('TEST PASSED')
            except AssertionError:
                print('TEST FAILED')

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_insert_single_record(self):
        luke = list(
            create_generator_from_dataset(self.dataset, 21)
        )[-1]
        ins = dbOps.store_xco2(
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
            print('TEST PASSED')
        except AssertionError:
            print('TEST FAILED')

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_bulk_dump(self):
        """Test Xco2.bulk_dump()"""
        session2 = dbOps.create_session(self.engine)
        util_truncate_table(session2)

        dbOps.bulk_dump(
            create_generator_from_dataset(self.dataset, 8)
        )
        rows = self.session.query(Xco2).count()
        try:
            self.assertEqual(rows, 8)
            print('TEST PASSED')
        except AssertionError:
            print('TEST FAILED')

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_violate_unique_constraint(self):
        """Test for integrity check"""
        luke = list(
            create_generator_from_dataset(self.dataset, 21)
        )[-1]
        ins1 = ins2 = Xco2(
            xco2=luke.xco2,
            timestamp=luke.timestamp,
            latitude=luke.latitude,
            longitude=luke.longitude
        )

        try:
            dbOps.store_xco2(
                ins1
            )
            self.assertRaises(
                IntegrityError,
                dbOps.store_xco2,
                ins2
            )
            print('TEST PASSED')
        except AssertionError:
            print('TEST FAILED')

    def tearDown(self):
        # if you want to keep the data in the db to make test using psql,
        # comment the line below
        util_truncate_table(self.session)
        del self.session
        pass

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        del cls.paths
        cls.dataset.close()


if __name__ == '__main__':
    unittest.main()
