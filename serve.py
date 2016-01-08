# coding=utf-8
import sys
from wsgiref import simple_server

__author__ = 'Lorenzo'

from src.webserver import app


_PORT = 5000

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', _PORT, app)
    print('Falcon serving at port: {port!s}'.format(port=_PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
