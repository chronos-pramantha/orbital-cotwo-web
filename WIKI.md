# PostGIS
## PostGIS How-tos
PostGIS is a quite wide extension for PostGRE: check the [features](http://www.postgis.us/downloads/postgis21_cheatsheet.html).
Full manual [here](http://postgis.net/docs/manual-dev).
It makes possible calculations over planar (geometry) or ellipsoidal (geography) spatial data types. In latest versions of PostGRE it can be activated as EXTENSION.

#### Install PostGRE SQL database on Ubuntu
```
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-9.3-postgis-2.1
```
See also [here](https://help.ubuntu.com/community/PostgreSQL)

Create a 'gis' and 'test' database and a 'gis' user with password 'gis' and privileges:
```
$> sudo -u postgres psql postgres

$psql> \password postgres;
(type password for 'root' user)

$psql> CREATE USER gis;
$psql> \password gis
(type password for the 'gis' user)

$psql> CREATE DATABASE gis;
$psql> GRANT ALL PRIVILEGES ON DATABASE gis TO gis;

$psql> CREATE DATABASE test;
$psql> GRANT ALL PRIVILEGES ON DATABASE test TO gis;

$psql> \connect gis
$psql> CREATE EXTENSION postgis;

$psql> \connect test
$psql> CREATE EXTENSION postgis;
```

Check if everything is ok:
```
$psql> \dt+ t_co2;
                     List of relations
 Schema | Name  | Type  | Owner |    Size    | Description
--------+-------+-------+-------+------------+-------------
 public | t_co2 | table | gis   | 8192 bytes |
(1 row)

$psql> \d+ t_co2;
                                                         Table "public.t_co2"
   Column    |            Type             |                     Modifiers                      | St
orage | Stats target | Description
-------------+-----------------------------+----------------------------------------------------+---
------+--------------+-------------
 id          | integer                     | not null default nextval('t_co2_id_seq'::regclass) | plain   |          |
 xco2        | double precision            |                                                    | plain   |          |
 timestamp   | timestamp without time zone |                                                    | plain   |          |
 coordinates | geography(Point,4326)       |                                                    | main    |          |
 pixels      | geometry(Point,3857)        |                                                    | main    |          |
Indexes:
    "t_co2_pkey" PRIMARY KEY, btree (id)
    "idx_t_co2_coordinates" gist (coordinates)
    "idx_t_co2_pixels" gist (pixels)
Has OIDs: no

$psql> SELECT * FROM information_schema.table_constraints WHERE table_name='t_co2';
 constraint_catalog | constraint_schema |    constraint_name    | table_catalog | table_schema | table_name | constraint_type |
--------------------+-------------------+-----------------------+---------------+--------------+------------+-----------------+
 gis                | public            | t_co2_pkey            | gis           | public       | t_co2      | PRIMARY KEY     | 
 gis                | public            | uix_time_coords       | gis           | public       | t_co2      | UNIQUE          | 
 gis                | public            | 2200_24316_1_not_null | gis           | public       | t_co2      | CHECK           | 
(3 rows)

```

#### Notes on Spatial Reference Systems

"Here's the catch. Using SRID 3785 is like recording coordinates in pixels rather than latitude/longitude. In order to specify a particular point on the globe, the numbers you use are the actual flat pixel distance across and down from the center pixel of the map. So POINT(-80 34) is not longitude -80, latitude 34. It's 80 pixels to the left of the center of the map, and 34 pixels up from the center.

Of course, to fully specify what POINT(-80 34) actually is on the globe, you have to specify how big the map is, so you know what scale you're working with. SRID 3785 defines the map to be 40075016.6856 pixels wide. This number is carefully chosen so that one pixel corresponds to one meter at the Equator. Since the map is that large, you can now see that POINT(-80 34) is actually very close to the center of the map, somewhere off the coast of west Africa, and nowhere near longitude -80, latitude 34, which is in the US.

Alright, so now the question is how do we perform distance queries when the data is stored in SRID 3785. The short answer is, you can IF your objects and distances are small. You have to do two things. First, you have to make sure you're specifying all the locations using SRID 3785 rather than latitudes and longitudes. Second, you have to undistort the distance based on the latitude, because a Mercator projection like SRID 3785 distorts size the further away you get from the Equator."
[Source](https://groups.google.com/d/msg/rgeo-users/mSuhjK2Jl8o/XtSEa0Sa0-YJ)

A good starter [article](http://daniel-azuma.com/articles/georails/part-7).

Choosing a [map projection (1)](https://source.opennews.org/en-US/learning/choosing-right-map-projection/) and [(2)](http://www.geo.hunter.cuny.edu/~jochen/gtech201/lectures/lec6concepts/map%20coordinate%20systems/how%20to%20choose%20a%20projection.htm).

EPSG [3857](http://wiki.openstreetmap.org/wiki/EPSG:3857) and popular [Web maps providers](http://gis.stackexchange.com/questions/48949/epsg-3857-or-4326-for-googlemaps-openstreetmap-and-leaflet).


#### create a PostGIS database
From psql command line:
```
CREATE DATABASE gisdb;
\connect gisdb;
-- Enable PostGIS (includes raster)
CREATE EXTENSION postgis;
-- Enable Topology
CREATE EXTENSION postgis_topology;
-- Enable PostGIS Advanced 3D 
-- and other geoprocessing algorithms
CREATE EXTENSION postgis_sfcgal;

-- OTHER EXTENSIONS
-- fuzzy matching needed for Tiger
CREATE EXTENSION fuzzystrmatch;
-- rule based standardizer
CREATE EXTENSION address_standardizer;
-- example rule data set
CREATE EXTENSION address_standardizer_data_us;
-- Enable US Tiger Geocoder
CREATE EXTENSION postgis_tiger_geocoder;
-- routing functionality
CREATE EXTENSION pgrouting;
-- spatial foreign data wrappers
CREATE EXTENSION ogr_fdw;

-- LIDAR support
CREATE EXTENSION pointcloud;
-- LIDAR Point cloud patches to geometry type cases
CREATE EXTENSION pointcloud_postgis;
```

#### create indexes
```
-- index on geometry field, to boost coordinates lookup
CREATE INDEX idx_table_geom
ON table
USING gist(geometry_field);

-- use of btree searching algorithm on other fields
CREATE INDEX idx_table_town
ON table
USING btree(some_field);
```

#### create a geometry column in PostGIS 2:
```
-- Add a point using the old constraint based behavior
SELECT AddGeometryColumn ('my_schema','my_spatial_table','geom_c',4326,'POINT',2, false);
```
Example: 

* Create a geometry column using the SRID 4326 (using PostGIS 2.0 syntax), to hold the GIS object:
```
ALTER TABLE table ADD COLUMN geom geometry(POINT,4326);
```
* Update the geometry column with the latitude and longitude of each point:
```
UPDATE table SET geom = ST_SetSRID(ST_MakePoint(longitude,latitude),4326);
```
* And create a spatial index:
```
CREATE INDEX idx_table_geom ON table USING GIST(geom);
```

#### create a geography column
```
CREATE TABLE testgeog(gid serial PRIMARY KEY, the_geog geography(POINT,4326) );
```

# Some Math
SQL query to retrieve all the points from a given distance from a point:
```
SELECT id, (
    6371 * acos (
        cos (radians(11.0))
        * cos( radians(latitude))
        * cos(radians(longitude) - radians(-172.0))
        + sin( radians(11.0))
        * sin radians(latitude)
        )
    ) AS distance 
    FROM xco2_table
    HAVING distance < 30
```

PostGIS query using a geometry column and the `GeometryFromText` function:
```
# Select all the geometry points into a given polygon
SELECT * FROM myTable WHERE 
    ST_Within(
       the_geom_column, 
       GeometryFromText (
           'POLYGON(
               (75 20,80 30,90 22,85 10,75 20)
            )', 4326
       )
    )
```

# Web server
- we are using [Falcon](http://falconframework.org)
See CHANGESLOG


# REST API
**Version 0.0.1**:

One endpoint:
`POST /co2/by/area/` accepts a [GeoJSON geometry](http://geojson.org/) defining a polygon and returns a GeoJSON feature collection of points with a `xco2` property 

See CHANGESLOG
