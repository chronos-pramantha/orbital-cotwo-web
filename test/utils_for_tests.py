# coding=utf-8
"""
This module contains utilities to be used to prepare data for tests
 setting up and tearing down.
"""
from random import randint

__author__ = 'Lorenzo'

from src.formatdata import create_generator_from_dataset
from src.xco2ops import xco2Ops
from src.xco2 import Xco2


# ##### UTILITIES FOR TESTS ##################################################
def util_populate_table(dataset, lentest):
    """
    Populate the t_co2 table with n rows

    :param numpyArray dataset:
    :param int lentest:
    :param Session session:
    :return list: tuples containing primary keys of points and areas
    """
    # create a generator from the first lentest records in the dataset
    luke = create_generator_from_dataset(dataset, lentest)

    samples = [
        xco2Ops.store_xco2(
            Xco2(
                xco2=d.xco2,
                timestamp=d.timestamp,
                latitude=d.latitude,
                longitude=d.longitude
            )
        ) for d in luke
    ]

    return samples


def util_truncate_table(session, table=[Xco2]):
    """Utility to drop table's content"""
    try:
        [session.query(t).delete() for t in table]
        session.commit()
    except:
        session.rollback()


def pick_random_sample(dataset, samples):
    i = i = randint(0, 19)
    test_point_pk, test_areas_pk = samples[i][0][0], samples[i][1]
    long, lat = dataset['longitude'][i], dataset['latitude'][i]
    return i, test_point_pk, test_areas_pk, long, lat

# ##### ############### ######################################################
