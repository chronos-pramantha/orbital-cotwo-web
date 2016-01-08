# coding=utf-8
import os
import unittest
import sqlite3

__author__ = 'Lorenzo'

from config.config import _PATH, t_name
from src.formatdata import createOCOpoint
from files.loadfiles import return_files_paths, return_dataset
from src.storedata import format_namedtuple, namedtuple_values_to_sql, go_execute
test_db = _PATH

# #todo: implement 'luke' as a Mock()


class DBtest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create a connection
        cls.conn = sqlite3.connect(test_db)
        # retrieve a data sample
        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])

    def setUp(self):
        # create a fake OCOpoint
        self.luke = createOCOpoint(**{
            'latitude': self.dataset['latitude'][0],
            'longitude': self.dataset['longitude'][0],
            'xco2': self.dataset['xco2'][0],
            'date': self.dataset['date'][0],
            }
        )

    def test_should_return_db_table_fields(self):
        """Test if the right table is created"""
        sql = 'pragma table_info({name!s})'.format(name=t_name)
        c = go_execute(sql)
        names = [tup[1] for tup in c.fetchall()]
        self.assertEqual(names, ['t_key', 'latitude', 'longitude', 'xco2', 'timestamp'])

    def test_should_format_namedtuple(self):
        """Test format_namedtuple decorator on namedtuple_values_to_sql"""
        func = format_namedtuple(namedtuple_values_to_sql, self.luke)
        self.assertTrue((callable(func)))

    def test_should_turn_nametuple_to_sql_statement(self):
        """ Test namedtuple_values_to_sql and its decorator"""
        sql = namedtuple_values_to_sql(self.luke)
        test = ('INSERT INTO table_xco2 (\'timestamp\', \'xco2\', \'latitude\', \'longitude\') '
                'VALUES (\'2014-09-06 01:41:45\', 395.0962829589844, -38.104153, -174.93721)')
        self.assertTrue(isinstance(sql, str))

    def test_should_store_using_go_execute(self):
        """Test making an insert in the db"""
        go_execute(namedtuple_values_to_sql(self.luke))

        # try to execute again same insert as above but should fail
        self.assertRaises(
            sqlite3.IntegrityError,
            go_execute,
            namedtuple_values_to_sql(self.luke)
        )

    def tearDown(self):
        del self.luke

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        del cls.paths
        cls.dataset.close()


if __name__ == '__main__':
    unittest.main()