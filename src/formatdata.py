#!/usr/bin/env python3
# coding=utf-8
"""
Retrieve data from netCDF4 files and store it into objects
"""
# ### patch for developing vm
import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
# ###########################

from collections import namedtuple
from datetime import datetime

__author__ = 'Lorenzo'


OCOpoint = namedtuple(
    'OCOpoint',
    ['timestamp', 'xco2', 'latitude', 'longitude']
)


def createOCOpoint(**data):
    """Take data for each point and create a nameptuples"""

    return OCOpoint(
        latitude=data['latitude'],
        longitude=data['longitude'],
        timestamp=datetime(*map(int, data['date'])),
        xco2=float(data['xco2'])
    )


def create_generator_from_dataset(ds):
    """
    Each file contains 30000+ relevations, loop over them and create a generator.

    :param nc4.Dataset ds:
    :return:
    """
    return (
        createOCOpoint(**{
            'latitude': ds['latitude'][0],
            'longitude': ds['longitude'][0],
            'xco2': ds['xco2'][0],
            'date': ds['date'][0],
        }) for i in range(len(ds['latitude'])))


def return_hdf_groups(ds):
    """
    Return HDF% groups in the dataset
    :param nc4.Dataset ds:
    :return: tuple of strings
    """
    def walk_tree(top):
        values = top.groups.values()
        yield values
        for value in top.groups.values():
            for children in walk_tree(value):
                yield children

    # print('GROUPS \n')
    groups = []
    for children in walk_tree(ds):
        for child in children:
            groups.append(child)
    return tuple(groups)


def return_data_format(ds):
    """
    Return format of the netCDF
    :param nc4.Dataset ds:
    :return: str
    """
    return ds.data_model


def return_dimensions(ds):
    """
    Return HDF5 dimensions in the dataset
    :param nc4.Dataset ds:
    :return: OrderedDict
    """
    # print('DIMENSIONS \n')
    return ds.dimensions


def return_variables(ds):
    """
    Return HDF5 variables in the dataset
    :param nc4.Dataset ds:
    :return: OrderedDict
    """
    return ds.variables


def return_attributes(ds):
    """
    Return HDF5 attributes in the dataset
    :param nc4.Dataset ds:
    :return: tuple
    """
    return tuple(
        [
            (name, getattr(ds, name))
            for name in ds.ncattrs()
        ]
    )


def return_variable_doc(ds, var):
    """

    :param str var:
    :return: str
    """
    return ds[var].__dict__




