# coding=utf-8
import geojson

__author__ = 'Lorenzo'


def get_coordinates_from_geojson(geojs):
    """Return coordinates from a GeoJSON Feature"""
    obj = geojson.loads(geojs)
    return geojson.utils.coords(obj)
