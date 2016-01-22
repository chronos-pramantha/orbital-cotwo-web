# coding=utf-8
"""
########## Functionality integration tests #############
This module contains tests that doesn't provide clean up.
After run this file, the test tables are populated, and to run
other tests must be manually truncated.
Consistency of data stored can be tested by entering queries from
psql or using the method below. It is useful to understand how the
popping-over algorithm works.
"""
from datetime import datetime
__author__ = 'Lorenzo'

from test.utils_for_tests import rand_coordinates, rand_data

TESTLENGTH = 1000  # set a number of iteration

# test functionality
TEST1 = (100, True)    # short test - random points from small portion of surface (1 square)
# test solidity (even increasing the number of points the number of area remains still)
TEST2 = (1000, True)  # long test - random points from small portion of surface (1 square)
# test scope (many points are created and many areas. Total plane should be around 33600 squares)
TEST3 = (10000, False) # long test - random points from all the cartesian plane


def test_should_store_a_new_area(rng, square):
    """Test insertion of a area alongside with a xco2 data"""
    from src.xco2ops import xco2Ops
    from src.xco2 import Xco2
    for _ in range(rng):
        # use squared params to limit to a limited portion
        longitude, latitude = rand_coordinates(squared=square)
        xco2 = Xco2(
            xco2=rand_data(),
            longitude=longitude,
            latitude=latitude,
            timestamp=datetime(1970, 1, 1)
        )
        xco2Ops.store_xco2(xco2)
    ########
    # RESULTS
    # After running this function (also multiple times) try the
    # following queries on the database:
    ########
    # SELECT t_co2.id, ST_X(pixels) as long, ST_Y(pixels) as lat, t_areas.data as geojson FROM t_co2, t_areas LIMIT 1;
    # SELECT ST_AsText(pixels), t_areas.data FROM t_co2, t_areas LIMIT 1;

    pass


def test_should_update_an_exisiting_area():
    from src.areasops import areasDbOps
    from src.spatial import spatialOps
    geometry = spatialOps.shape_geometry(rand_coordinates()[0], rand_coordinates()[1])
    square = spatialOps.shape_aoi(geometry)
    areasDbOps.store_area(geometry)


def test_should_find_all_xco2_points_in_aoi():
    pass


def test_should_get_aoi_that_contains_():
    pass


if __name__ == '__main__':

    """Choose a test from above"""
    rng, square = TEST1
    try:
        test_should_store_a_new_area(rng, square)
    except KeyboardInterrupt as e:
        raise e
