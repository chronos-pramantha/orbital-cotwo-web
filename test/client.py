# coding=utf-8
"""
Basic HTTP client and a Thread Pooling function to manage multiple requests
"""
import urllib.request
import urllib.parse

from config.secret import secret


__author__ = 'Lorenzo'


def _request(url, data=None):
    """
    Build the Request object to send to JSON-RPC API.

    :param str url: complete endpoint
    :param dict data: data for the POST body
    :return: Request object
    """
    if data:
        req = urllib.request.Request(
            url,
            data.encode("utf-8")  # encode to bytes
        )
        req.add_header("X-Auth-Token", secret)
        req.add_header("Accept", 'application/json')
        req.add_header("Content-Type", 'application/json')
    else:
        req = urllib.request.Request(url)
    return req


def _response(request):
    """
    Open the URL in the Request object.

    :param Request request: a urllib Request object
    :return tuple: (content, http_code)
    """
    # "Content-Length": str(len(data))

    with urllib.request.urlopen(request) as response:
        status = response.getcode()
        # print(status, response.info(), )
        data = response.read().decode('utf-8')

    # print(data)
    return status, data
