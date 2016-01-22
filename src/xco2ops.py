# coding=utf-8
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

__author__ = 'Lorenzo'

from src.xco2 import Xco2
from src.dbproxy import dbProxy
from src.areasops import areasDbOps, areasAlgorithm


class xco2Ops(dbProxy):
    """
    Generic DB operations on the Xco2 table.
    """
    @classmethod
    def store_xco2(cls, xobject):
        """
        Main function to the database when storing Xco2 data.

        INSERT procedure is as follow:
            - insert point > belong the point to any known area?
            - if Y > INSERT point
            - if N > create area with center=point using shape_aoi()

        At database initialization, this method is called to populate both
         the Xco2 and the Areas tables following the pop-above algorithm.

        Store a Xco2 relevation and store or update its related Area of Interest.
        :param xobject: a Xco2 object
        :return tuple: (pkey_xco2, pkey_area, )
        """
        from src.spatial import spatialOps
        geometry = spatialOps.shape_geometry(xobject.longitude, xobject.latitude)
        ins = Xco2.__table__.insert().values(
            xco2=xobject.xco2,
            timestamp=xobject.timestamp,
            geometry=geometry
        )
        try:
            result = cls.alchemy.execute(ins)
            aoi = areasDbOps.store_area(geometry, xobject.xco2)
        except IntegrityError as e:
            # integrity error happens when a datum is updated or two data are
            # are rounded to the same coordinates (Postgis maximum tolerance is -xxx.yyy)
            # compare dates, if record is more recent store it and archive the older one
            raise e
        except Exception as e:
            raise e

        return result.inserted_primary_key, aoi.pk

    @classmethod
    def bulk_dump(cls, objs_generator):
        """
        Dump in the database big amounts of objects from a generator.

        # #todo: refactor using session and add_all()

        :param iter objs_generator:
        """
        while True:
            try:
                obj = next(objs_generator)
                new = Xco2(
                    xco2=obj.xco2,
                    timestamp=obj.timestamp,
                    latitude=obj.latitude,
                    longitude=obj.longitude
                )
                cls.store_xco2(new)
            except StopIteration:
                return
            except Exception as e:
                raise e

    @classmethod
    def single_point_query(cls, long, lat, mode='geometry'):
        """
        Build a query on Geometry or Geography field.

        :param float long: longitude
        :param float lat: latitude
        :param str mode: geometry or geography
        :return Query: query object
        """
        from src.spatial import spatialOps
        func = 'shape_' + mode if mode in ('geometry', 'geography',) else None
        if func:
            fltr = getattr(spatialOps, func)(long, lat)
            query = select([Xco2]).where(
                Xco2.coordinates == fltr
            )
            result = cls.alchemy.execute(query).fetchone()
        else:
            raise ValueError('mode can be only geometry or geography')
        return result

__all__ = [
    'store_xco2'
]