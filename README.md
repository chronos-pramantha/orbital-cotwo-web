# A Web interface for OCO2 data

## Run the code
* install requirements.txt (Python 3.4+ required)
* install PostgreSQL and PostGIS extension. In Ubuntu:  
```
# depending on you Python version you could need also 
# pythonX.Y-dev and /or libpg-dev
sudo apt-get install postgresql postgresql-contrib
# substitute X.y with the version of potegresql installed
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

* run `python src/xco2.py` to create database table
* download files from NASA using the script in `files/` (you can use the Python script or `wget` with the txt file)
* run `main.py` to dump data from files to db
* run `serve.py` to start the server
* try `curl 127.0.0.1:5000`

## Run tests
* `python test/tests_<some name>` to test functionality (it uses the `test` database)

## Status
* Refactoring to PostGRE/PostGIS support [DONE]
* Dump of data procedure complete [DONE]
* BUG in storing method [FIXED]
* Create a class for db operations [DONE]
* Starting querying tests [DONE]
* *TO BE IMPLEMENTED*: The server accepts POST request at `/oco2/by/area`. It needs a GeoJSON to be passed in the request's body.

## To-do
* [PostGRE-PostGIS](http://postgis.net/) support
* Write more test queries
* Design the REST interface
* Set up the Web server

## Wiki
see the `WIKI.md` file

## Notes 
* Developed on Python 3.5.1 and Postgre 9.3