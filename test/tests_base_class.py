# coding=utf-8
import unittest

__author__ = 'Lorenzo'

from src.xco2 import Xco2
from src.dbops import start_postgre_engine
from files.loadfiles import return_files_paths, return_dataset
from src.formatdata import createOCOpoint


class TestXco2TableClass(unittest.TestCase):
    """
Test the object mapper to table t_co2.
"""
    @classmethod
    def setUpClass(cls):
        print(cls.__doc__)
        _, cls.engine = start_postgre_engine('test', False)
        cls.conn = cls.engine.connect()

        cls.paths = return_files_paths()
        cls.dataset = return_dataset(cls.paths[0])

        # create an OCOpoint from the first record in the first file
        cls.luke = createOCOpoint(**{
            'latitude': cls.dataset['latitude'][0],
            'longitude': cls.dataset['longitude'][0],
            'xco2': cls.dataset['xco2'][0],
            'date': cls.dataset['date'][0],
            }
        )

    def setUp(self):
        pass

    def test_should_create_a_xco2_obj(self):
        """Create a Xco2 object using the constructor"""
        new = Xco2(
            xco2=self.luke.xco2,
            timestamp=self.luke.timestamp,
            latitude=self.luke.latitude,
            longitude=self.luke.longitude
        )
        try:
            repr(new)
            str(new)
        except Exception as e:
            self.assertTrue(False)

    def test_should_calculate_a_geometry_value(self):
        """Test: SELECT * FROM ST_GeomFromEWKT('POINT(latitude longitude)'); """
        geom_EWKT = 'SRID=3857;POINT(-174.9372100830078 -38.10415267944336)'
        q = "SELECT ST_GeomFromEWKT('{}');".format(geom_EWKT)
        #print(q)
        try:
            result = self.conn.execute(q)
        except Exception:
            raise Exception('Cannot perform function ST_GeomFromEWKT. '
                            'Check if PostGIS extensions are installed.')
        self.assertEqual(
            str([r for r in result][0][0]),
            '0101000020110F0000000000A0FDDD65C0000000E0540D43C0'
        )

    def test_should_calculate_a_geography_value(self):
        """Test: SELECT * FROM ST_GeogFromText('SRID;POINT(latitude longitude)'); """
        geog_EWKT = 'SRID=4326;POINT(-174.9372100830078 -38.10415267944336)'
        q = "SELECT ST_GeogFromText('{}');".format(geog_EWKT)
        try:
            result = self.conn.execute(q)
        except Exception:
            raise Exception('Cannot perform function ST_GeomFromEWKT. '
                            'Check if PostGIS extensions are installed.')
        self.assertEqual(
            str([r for r in result][0][0]),
            '0101000020E6100000000000A0FDDD65C0000000E0540D43C0'
        )

    def test_should_return_db_table_fields(self):
        """Test if the right fields are created in the table"""
        names = [k for k in Xco2.__table__.columns.keys()]
        #print(names)
        self.assertEqual(names, ['id', 'xco2', 'timestamp', 'coordinates', 'pixels'])

    def test_should_return_a_table_insert_string(self):
        ins = Xco2.__table__.insert()
        test = (
            'INSERT INTO t_co2 (id, xco2, timestamp, coordinates, pixels) '
            'VALUES (:id, :xco2, :timestamp, ST_GeogFromText(:coordinates), '
            'ST_GeomFromEWKT(:pixels))'
        )
        self.assertEqual(test, str(ins))
        #print(str(ins))

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        del cls

if __name__ == '__main__':
    unittest.main()
