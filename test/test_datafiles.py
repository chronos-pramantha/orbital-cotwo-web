# coding=utf-8
"""
Tests for the data loading from files (netCDF4).
See <http://pyhogs.github.io/intro_netcdf4.html>
"""
import unittest
import netCDF4 as nc4

__author__ = 'Lorenzo'

from files.loadfiles import return_files_paths, return_dataset


class TestDataFiles(unittest.TestCase):
    """
Test files' paths.

"""
    @classmethod
    def setUpClass(cls):
        print(cls.__doc__)

    def setUp(self):
        self.paths = return_files_paths()

    def test_get_files_paths(self):
        paths = return_files_paths()
        self.assertTrue(isinstance(paths, list))
        self.assertTrue(len(paths) >= 2)
        del paths

    def test_open_a_random_dataset(self):
        d = return_dataset()
        self.assertTrue(isinstance(d, nc4.Dataset))
        d.close()

    def test_open_a_specified_dataset(self):
        d = return_dataset(self.paths[1])
        self.assertTrue(isinstance(d, nc4.Dataset))
        d.close()

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()

