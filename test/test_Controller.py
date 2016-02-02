# coding=utf-8
import unittest
import geojson

__author__ = 'Lorenzo'

from src.areasops import Controller
from src.dbproxy import start_postgre_engine
from test.utils_for_tests import rand_polygon, rand_coordinates
from src.spatial import spatial
from src.dbproxy import dbProxy


class TestController(unittest.TestCase):
    """
    Test the Controller. The class that receive and elaborate the request.
    """
    REFACTOR = True

    @classmethod
    def setUpClass(cls):
        print(cls.__doc__)
        _, cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()

    def setUp(self):
        """Create a random square."""
        geojson = {
                "geometry": {
                    "type": "Polygon",
                    "coordinates": rand_polygon()
                }
            }
        # simulate a single view/area
        self.polygon_avg = spatial.from_list_to_ewkt(geojson['geometry']['coordinates'])
        # simulate a view with 3 areas
        p = (-14, -68)  # rand_coordinates()
        self.polygon_big, _ = spatial.shape_aoi(p, size=8)  # spatial.from_list_to_ewkt(rand_polygon(size=12))
        # simulate a random point

        self.point = spatial.shape_geometry(p[0], p[1])

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_initialize_controller(self):
        print('TEST1')
        controller = Controller(self.polygon_avg)
        try:
            print(str(controller))
            #print(repr(controller))
            print('TEST PASSED')
        except:
            print('TEST FAILED')

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_print_coordinates(self):
        print('TEST2')
        controller = Controller(self.polygon_avg)
        try:
            #print(repr(controller))
            print(controller.geo_object.__geo_interface__)
            #print(controller.geo_object.bounds)
            print('TEST PASSED')
        except:
            print('TEST FAILED')

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_find_all_the_areas_from_a_view(self):
        """Should find all the rows in t_areas that are contained in the polygon"""
        print('TEST3')
        controller = Controller(self.polygon_big)
        # find all the areas contained in the view
        count = dbProxy.alchemy.execute(
            'SELECT count(*) FROM t_areas WHERE ST_Contains(%s, aoi)',
            ((controller.geometry, ), )
        ).first()
        print('FOUND: ', count[0])
        results = dbProxy.alchemy.execute(
            'SELECT id, aoi, center, data FROM t_areas WHERE ST_Contains(%s, aoi)',
            ((controller.geometry, ), )
        ).fetchall()
        for r in results:
            print(r)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_return_controller_center(self):
        controller = Controller(self.polygon_big)
        print(controller.geo_object.__geo_interface__['coordinates'])
        print(controller.center)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_return_controller_primary_keys(self):
        controller = Controller(self.polygon_big)
        print(controller.pks)

    @unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_find_closest_centers(self):
        print('TEST4')
        controller = Controller(self.point)
        closest = controller.what_are_the_closest_centers_to_(controller.geometry)
        print(closest)

    #@unittest.skipIf(REFACTOR, 'Refactoring')
    def test_should_return_all_the_xco2_in_a_geometry(self):
        # create a controller
        controller = Controller(self.polygon_big)
        #print(self.polygon_big)
        # find the areas contained by controller's view
        controller.which_areas_contains_this_polygon()
        # return the JSON points contained by the areas
        #print(areas)
        json = controller.serialize_features_from_database()

        print(json)


    def tearDown(self):
        del self

    @classmethod
    def tearDownClass(cls):
        del cls

if __name__ == '__main__':
    unittest.main()
