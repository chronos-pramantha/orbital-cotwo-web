# coding=utf-8
import unittest
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError


__author__ = 'Lorenzo'

from src.xco2 import start_postgre_engine, Xco2
from files.loadfiles import return_files_paths, return_dataset
from src.formatdata import create_generator_from_dataset, bulk_dump


# #todo: implement 'luke' as a Mock()

REFACTOR = False  # Flag to be set during refactoring for partial tests
TEST_LENGTH = 20  # Number of rows to insert in the test db


class DBtest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()

        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])

    def util_create_session(self, engine):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        return session

    def util_populate_table(self, session):
        # create an OCOpoint from the first record in the first file
        self.test_length = TEST_LENGTH
        luke = create_generator_from_dataset(self.dataset, self.test_length)

        session.add_all(
            [
                Xco2(
                    xco2=d.xco2,
                    timestamp=d.timestamp,
                    latitude=d.latitude,
                    longitude=d.longitude
                ) for d in luke
            ]
        )

        session.commit()

    def util_drop_table(self, session):
        """Utility to drop table's content"""
        try:
            session.query(Xco2).delete()
            session.commit()
        except:
            session.rollback()

    def setUp(self):
        self.session = self.util_create_session(self.engine)
        self.util_populate_table(self.session)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_find_the_records_in_the_db(self):
        """Perform a Select to check the data inserted above"""
        rows = self.session.query(Xco2).count()
        self.assertEqual(rows, self.test_length)
        #print(rows)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_create_xco2_obj_from_select_query(self):
        #
        pass

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_compare_data_between_db_and_dataset(self):
        ten = self.session.query(Xco2).limit(10)
        lst = list(create_generator_from_dataset(self.dataset, 10))
        for i, l in enumerate(lst):
            self.assertAlmostEqual(l.xco2, ten[i].xco2, delta=0.0000001)
            self.assertEqual(l.timestamp, ten[i].timestamp)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_insert_single_record(self):
        luke = list(
            create_generator_from_dataset(self.dataset, 21)
        )[-1]
        ins = Xco2.__table__.insert().values(
            xco2=luke.xco2,
            timestamp=luke.timestamp,
            coordinates=Xco2.shape_geography(
                luke.latitude,  luke.longitude),
            pixels=Xco2.shape_geometry(
                luke.latitude, luke.longitude)
        )
        self.conn.execute(ins)
        rows = self.session.query(Xco2).count()
        self.assertEqual(rows, self.test_length + 1)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_bulk_dump(self):
        """Test Xco2.bulk_dump()"""
        session2 = self.util_create_session(self.engine)
        self.util_drop_table(session2)

        bulk_dump(
            self.session,
            create_generator_from_dataset(self.dataset, 8)
        )
        rows = self.session.query(Xco2).count()
        self.assertEqual(rows, 8)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_violate_unique_constraint(self):
        """Test for integrity check"""
        luke = list(
            create_generator_from_dataset(self.dataset, 21)
        )[-1]
        ins1 = ins2 = Xco2.__table__.insert().values(
            xco2=luke.xco2,
            timestamp=luke.timestamp,
            coordinates=Xco2.shape_geography(
                luke.latitude,  luke.longitude),
            pixels=Xco2.shape_geometry(
                luke.latitude, luke.longitude)
        )
        self.conn.execute(ins1)

        self.assertRaises(
            IntegrityError,
            self.conn.execute,
            ins2
        )

    def tearDown(self):
        # if you want to keep the data in the db to make test using psql,
        # comment the line below
        self.util_drop_table(self.session)
        del self.session
        pass

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        del cls.paths
        cls.dataset.close()


if __name__ == '__main__':
    unittest.main()