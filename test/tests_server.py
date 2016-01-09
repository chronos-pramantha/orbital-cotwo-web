# coding=utf-8
import sys
import unittest
import subprocess
import json

__author__ = 'Lorenzo'

from serve import _HOST, _PORT
from test.client import _request, _response


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.url = 'http://{host}:{port}/'.format(host=_HOST, port=_PORT)
        self.aoi = self.url + 'co2/by/area'

    def test_should_get_homepage(self):
        """Test GET /"""
        req = _request(self.url)
        resp = _response(req)

        print(resp[1])

        self.assertTrue(resp[0] == 200)

    def test_should_return_the_mock_endpoint_for_by_area(self):
        """Test POST /co2/by/area.

        A GeoJSON is passed as POST data"""
        url = 'http://localhost:5000/co2/by/area'
        # area of interest is defined as a GeoJSON polygon
        # complete this JSON with points in the database
        data = json.dumps(
            {
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [62.5, 169.0],
                            [62.5, 169.3],
                            [62.9, 169.3],
                            [62.9, 169.0],
                            [62.5, 169.0]
                        ]
                    ]
                }
            })

        req = _request(url, data)
        resp = _response(req)
        print(resp[1])

        self.assertTrue(resp[0] == 200)
        self.assertTrue(json.dumps(resp[1] == data))


if __name__ == '__main__':
    unittest.main()
