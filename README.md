# A Web micro-service for OCO2 data

This micro-service provides map clients with **geolocated Web-compliant data**. 
Data published by *NASA/JPL's Orbital Carbon Observatory*  mission can be then easily edited into a map for Web-browsers using popular map providers' API.
This tool can be modified to serve any kind of geolocated data from an Highly Distributed Filesystem source, for further information contact the author.

## License
See LICENSE

All rights on the data are in the property of the Owner.

## Data pipeline
This micro-service implements a **data pipeline** from highly distributed file system (HDF5) to SQL/GIS database, serving results from geoqueries into GeoJSON format using Falcon high-perfomance Web server.
It implements a simple algorithm to have fast access to the totality of Earth's surface (using projection 3857).
This is a beta version, the most advanced features are not yet fully implemented.

## Install the database and server (Linux Ubuntu or Debian)
* install `requirements.txt` (Python 3.4+ required)
* install PostgreSQL and PostGIS extension. In Ubuntu:  
```
# depending on you Python version you could need also 
# pythonX.Y-dev and/or libpg-dev
sudo apt-get install postgresql postgresql-contrib
# check that Postgres is running
sudo service postgresql status
# substitute X.Y with the version of potegresql installed
sudo apt-get install postgresql-server-dev-X.Y
# substitute Z.W with the version of postgis installed
sudo apt-get install postgresql-X.Y-postgis-Z.W
```
See also [here](https://help.ubuntu.com/community/PostgreSQL)

Create a 'gis' and 'test' database and a 'gis' user with password 'gis' and privileges:
```
-- enter psql command line
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

* run `python src/xco2.py` to create database tables

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
-------------+-----------------------------+----------------------------------------------------+---------+----------+
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

## Dump the data and run the code

* download files from NASA using the script in `files/` (you can use the Python script or `wget` with the txt file; you don't need to download them all, some of them are enough for a test)
* run `main.py` to dump data from files to db
* run `serve.py` to start the server
* try `curl 127.0.0.1:5000`

## Run tests
* `python3 test/run_test.py` to run the full suite (it uses the `test` database). Unit tests to test general functionality of the code.
* `python3 test/test_integration1_initialize.py` to test basic operations (it uses the `test` database). Some data is inserted and can be queried, follow the instructions printed on the screen
* You can use: 
```
curl 127.0.0.1:5000/co2/by/polygon -H 'X-Auth-Token: abc' -H 'Content-Type: application/json' -d '{"geometry": {"type": "Polygon", "coordinates": [ [[-18.0, -64.0], [-10.0, -64.0],[-10.0, -72.0], [-18.0, -72.0],[-18.0, -64.0]]]}}'
```
It should return all the points contained in the given geometry (choose a geometry that actually grab some data from your test sample, or you will have a void response).

## Status
* Refactoring to PostGRE/PostGIS support [DONE]
* Dump of data procedure complete [DONE]
* BUG in storing method [FIXED]
* Create a class for db operations [DONE]
* Starting querying tests [DONE]
* The server accepts POST request at `/co2/by/polygon`. It needs a GeoJSON to be passed in the request's body [DONE] 

## To-do
* <s>[PostGIS](http://postgis.net/) support</s>
* <s>Write more test queries</s>
* <s>Implement a caching/lookup/aggregation table for the main table</s>
* <s>Design a basic REST interface</s>
* <s>Set up a basic Web server</s>

## Wiki
see the `WIKI.md` file

## Notes 
* Developed on Python 3.5.1 and Postgre 9.3, on Ubuntu Trusty Tahr 64bit
* Python dependencies require different packages to be installed via `apt-get` in your Linux system (for example `netcdf4` requires `libhdf5-serial-dev`, `netcdf-bin`
   and `libnetcdf-dev`; `psycopg2` may need `pglib-dev`; etc.)