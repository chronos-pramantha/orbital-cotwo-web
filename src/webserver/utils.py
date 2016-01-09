# coding=utf-8
import geojson

__author__ = 'Lorenzo'


def get_coordinates_from_geojson(geojs):
    """Return coordinates from a GeoJSON Feature"""
    obj = geojson.loads(geojs)
    return geojson.utils.coords(obj)


def build_a_select(coords):
    # just a placeholder query, works only with coordinates in the
    # north-eastern quarter
    return (
        'SELECT latitude,longitude, xco2 from table_xco2 WHERE'
        '((latitude > {} and latitude < {}) and (longitude > {} and longitude < {}))'
    ).format(coords[0][0], coords[1][0], coords[0][1], coords[1][1])