# coding=utf-8
"""
Test data formatting from files to objects
"""
import unittest
import netCDF4 as nc4

# ### patch for developing vm
import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
# ###########################

__author__ = 'Lorenzo'

from files.loadfiles import return_dataset
from files.loadfiles import return_files_paths


class DataFormat(unittest.TestCase):
    def setUpClass(cls):
        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])

    def test_create_objects_from_netcdf(self):
        from src.formatdata import createOCOpoint
        createOCOpoints(self.dataset)

    def tearDownClass(cls):
        del cls.paths
        cls.dataset.close()


if __name__ == "__main__":
    unittest.main()
