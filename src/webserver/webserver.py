# coding=utf-8
import falcon
import json

__author__ = 'Lorenzo'

from src.webserver.utils import get_coordinates_from_geojson


class Xco2:
    """Long-living REST resource class.

    Use only POST method.
    """
    allowed = ('area', )

    def on_post(self, req, resp):
        """Handles POST requests"""
        resp.status = falcon.HTTP_200
        # grab 'geojson' from req.context
        # gather the needed resources
        # create a dictionary in GeoJSON format in 'result' for req.context
        aoi = req.context['geojson']
        from src.webserver.utils import build_a_select
        coords = [g for g in list(get_coordinates_from_geojson(aoi))[:3]]
        coords = (coords[0], coords[2], )

        from src.storedata import go_execute
        results = go_execute(build_a_select(coords))

        req.context['result'] = str([r for r in results])


class Hello:
    """Hello class for homepage"""
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('Falcon is flying.\n'
                     'Hello!\n')


# instantiate the long-living resource class for the server
class_ = Xco2()
hello = Hello()

#
# ##### Middleware pipe: Auth, Check, Translate ##############################
#


class AuthMiddleware:
    """Check token in request's header"""
    def process_request(self, req, resp):
        # check auth for POST or PUT methods
        if req.method in ('POST', 'PUT'):
            token = req.get_header('X-Auth-Token')
            project = req.get_header('X-Project-ID')

            def _token_is_valid(token, project):
                from config.secret import secret
                if token == secret:
                    req.context['authorized'] = True
                    return req.context['authorized']
                return False

            if token is None:
                description = ('Please provide an auth token '
                               'as part of the request.')

                raise falcon.HTTPUnauthorized('Auth token required',
                                              description,
                                              href='http://example.com/auth')

            if not _token_is_valid(token, project):
                description = ('The provided auth token is not valid. '
                               'Please request a new token and try again.')

                raise falcon.HTTPUnauthorized('Authentication required',
                                              description,
                                              href='http://example.com/auth',
                                              scheme='Token; UUID')


class RequireJSON(object):
    """Check if the content type in the request is valid"""
    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports requests encoded as JSON.',
                href='http://docs.examples.com/api/json')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.',
                    href='http://docs.examples.com/api/json')


class JSONTranslator:
    """Middleware to pre-process request's body and check if JSON is valid"""
    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Request body is void, nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['geojson'] = body.decode('utf-8')
            # #todo: use geojson.is_valid
            json.loads(req.context['geojson'])
        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'])

#
# ##### Define the app
#
app = falcon.API(middleware=[
    AuthMiddleware(),
    RequireJSON(),
    JSONTranslator(),
])

#
# ##### Define routes
#
app.add_route('/co2/by/area', class_)
app.add_route('/', hello)

