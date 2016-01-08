# coding=utf-8
"""
Basic HTTP client and a Thread Pooling function to manage multiple requests
"""
import urllib.request
import urllib.parse
import json

from secret import _KEY
from exceptions import ConnectionFault

__author__ = 'Lorenzo'


def _request(url, data=None):
    """
    Build the Request object to send to JSON-RPC API.

    :param str url: complete endpoint
    :param dict data: data for the POST form
    :return: Request object
    """
    if data:
        req = urllib.request.Request(
            url,
            json.dumps(data).encode("utf-8"),
            {
                "X-Starfighter-Authorization": _KEY,
                "accept-encoding": "gzip",
                "content-type": "application/json"
            }
        )
    else:
        req = urllib.request.Request(url)
    return req


def _response(request):
    """
    Open the URL in the Request object.

    :param Request request: a urllib Request object
    :return tuple: (content, http_code)
    """
    with urllib.request.urlopen(request) as response:
        status = response.getcode()
        # print(status, response.info(), )
        data = json.loads(
            response.read().decode('utf-8')
        )
    # print(data)
    if status == 200 and data["ok"]:
        return data, status
    elif status == 200 and not data["ok"]:
        raise ValueError('client._response() - Server response is not good ' +
                         json.dumps(data))
    else:
        raise ConnectionFault('client._response() - Connection Error: ' +
                              str(response.getcode()))


