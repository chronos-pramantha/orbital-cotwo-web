# coding=utf-8
import unittest
from sqlalchemy.orm import Session, sessionmaker


__author__ = 'Lorenzo'

from src.xco2 import start_postgre_engine, Xco2
from files.loadfiles import return_files_paths, return_dataset
from src.formatdata import create_generator_from_dataset, bulk_dump


# #todo: implement 'luke' as a Mock()


class DBtest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()

        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])

        Session = sessionmaker()
        Session.configure(bind=cls.engine)
        cls.session = Session()

    def setUp(self):
        self.util_populate_table()

    def util_populate_table(self):
        # create an OCOpoint from the first record in the first file
        self.test_length = 20
        self.luke = create_generator_from_dataset(self.dataset, self.test_length)

        self.session.add_all(
            [
                Xco2(
                    xco2=d.xco2,
                    timestamp=d.timestamp,
                    coordinates=Xco2.shape_geography(
                        d.latitude,  d.longitude),
                    pixels=Xco2.shape_geometry(
                        d.latitude, d.longitude)
                ) for d in self.luke
            ]
        )

        self.session.commit()

    def util_drop_table(self):
        """Utility to drop table's content"""
        try:
            self.session.query(Xco2).delete()
            self.session.commit()
        except:
            self.session.rollback()

    def test_should_find_the_records_in_the_db(self):
        """Perform a Select to check the data inserted above"""
        rows = self.session.query(Xco2).count()
        self.assertEqual(rows, self.test_length)
        #print(rows)

    def test_compare_data_between_db_and_dataset(self):
        ten = self.session.query(Xco2).limit(10)
        lst = list(self.luke)[:9]
        for i, l in enumerate(lst):
            self.assertAlmostEqual(l.xco2, ten[i].xco2, delta=0.0000001)
            self.assertEqual(l.timestamp, ten[i].timestamp)

    def test_bulk_dump(self):
        """Test Xco2.bulk_dump()"""
        bulk_dump(
            self.session,
            create_generator_from_dataset(self.dataset, 8)
        )
        rows = self.session.query(Xco2).count()
        self.assertEqual(rows, 28)

    def tearDown(self):
        # if you want to keep the data in the db to make test using psql,
        # comment the line below
        self.util_drop_table()
        pass

    @classmethod
    def tearDownClass(cls):
        del cls.session
        cls.conn.close()
        del cls.paths
        cls.dataset.close()


if __name__ == '__main__':
    unittest.main()