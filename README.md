# A Web interface for OCO2 data

## Run the code
* install requirements (Python 3.3+ required)
* install PostGRE SQL and PostGIS extensions as described in `WIKI.md` 
* run `python src/xco2.py` to create database table
* download files from NASA using the script in `files/` (you can use the Python script or `wget` with the txt file)
* run `main.py` to dump data from files to db
* run `serve.py` to start the server
* try `curl 127.0.0.1:5000`

## Run tests
* `python test/tests_<some name>` to test functionality (use the `test` database)

## Status
* Refactoring to PostGRE/PostGIS support [DONE]
* Dump of data procedure complete [DONE]
* Starting querying tests
* *TO BE IMPLEMENTED*: The server accepts POST request at `/oco2/by/area`. It needs a GeoJSON to be passed in the request's body.

## To-do
* [PostGRE-PostGIS](http://postgis.net/) support
* Write test queries
* Design the REST interface
* Set up the Web server

## Wiki
see the `WIKI.md` file