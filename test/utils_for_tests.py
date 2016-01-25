# coding=utf-8
"""
This module contains utilities to be used to prepare data for tests
 setting up and tearing down.
"""
from random import randint, randrange, uniform

__author__ = 'Lorenzo'

from src.formatdata import create_generator_from_dataset
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

    samples = []
    for d in luke:
        new = Xco2(
            xco2=d.xco2,
            timestamp=d.timestamp,
            latitude=d.latitude,
            longitude=d.longitude
        )
        samples.append(
            new.store_xco2()
        )

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
    test_point_pk, test_areas_pk = samples[i][0], samples[i][1]
    long, lat = dataset['longitude'][i], dataset['latitude'][i]
    return i, test_point_pk, test_areas_pk, long, lat


def rand_polygon(size=1.4):
    """
    Generate a random polygon in the NE quadrant.
    :param float size: the size of the polygon side in degrees
    :return list: a GEOjson coordinates list
    """
    polygon = list()
    nw = [round(uniform(0, 180.000), 4), round(uniform(0, 90.000), 4)]
    polygon.append(nw)
    polygon.append([nw[0] + size, nw[1]])
    polygon.append([nw[0] + size, nw[1] - size])
    polygon.append([nw[0], nw[1] - size])
    polygon.append(nw)
    return polygon


def rand_coordinates(squared=False):
    if squared:
        # generate coordinates only in one AoI (a square of 1.4 degree of size)
        return uniform(-136.000, -134.600), uniform(-35.000, -33.600)
    else:
        # generate random coords
        return uniform(-180.000, 179.000), uniform(-90.000, 89.000)


def rand_data():
    return uniform(285.000, 400.000)

# ##### ############### ######################################################
