# coding=utf-8
import os
import netCDF4 as nc4

__author__ = 'Lorenzo'

_NC4_FILES = os.path.join(os.path.dirname(__file__), 'nc4')


def return_files_paths():
    """Walk the directory and return a list of NC4 files' paths"""
    return [
        os.path.join(_NC4_FILES, n)
        for n in tuple(os.walk(_NC4_FILES))[0][2]
        if n.endswith('.nc4')
    ]


def return_dataset(path=None):
    """Pick a file path and return a DataSet object, if path is not specified
    return the first file"""
    if not path:
        return nc4.Dataset(return_files_paths()[0], 'r')
    return nc4.Dataset(path, 'r')





