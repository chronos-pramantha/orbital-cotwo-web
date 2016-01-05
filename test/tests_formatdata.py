# coding=utf-8
"""
Test data formatting from files to objects
"""
import unittest
import netCDF4 as nc4
from datetime import datetime

# ### patch for developing vm
import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
# ###########################

__author__ = 'Lorenzo'

from files.loadfiles import return_dataset
from files.loadfiles import return_files_paths
from src.formatdata import createOCOpoint

class DataFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])
        cls.length = len(cls.dataset['latitude'])

    def test_should_count_attribute_lines(self):
        print(len(self.dataset['latitude']))

    def test_should_create_one_object(self):
        """Create an object from the first line of data"""
        luke = createOCOpoint(**{
            'latitude': self.dataset['latitude'][0],
            'longitude': self.dataset['longitude'][0],
            'xco2': self.dataset['xco2'][0],
            'date': self.dataset['date'][0],
        }
        )
        self.assertEqual(luke.latitude, self.dataset['latitude'][0])
        self.assertEqual(luke.longitude, self.dataset['longitude'][0])
        self.assertEqual(luke.xco2, self.dataset['xco2'][0])
        self.assertEqual(luke.timestamp, datetime(*map(int, self.dataset['date'][0])))

    def test_create_objects_from_netcdf(self):
        luke = (createOCOpoint(**{
            'latitude': self.dataset['latitude'][i],
            'longitude': self.dataset['longitude'][i],
            'xco2': self.dataset['xco2'][i],
            'date': self.dataset['date'][i],
        }) for i in range(5))

        for p in luke:
            print(p)
            try:
                next(luke)
            except StopIteration:
                break

    @classmethod
    def tearDownClass(cls):
        del cls.paths
        cls.dataset.close()


if __name__ == "__main__":
    unittest.main()
