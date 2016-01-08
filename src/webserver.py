# coding=utf-8
import falcon
import json

__author__ = 'Lorenzo'


def max_body(limit):
    """Decorator to check content length"""

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class Xco2:
    """Long-living REST resource class.

    Use only POST method.
    """
    def __new__(cls):
        # allowed endpoints for this URI
        cls.allowed = ('area', )

    def on_post(self, req, resp, endpoint):
        """Handles POST requests"""
        if endpoint in self.allowed:
            resp.status = falcon.HTTP_200
            # grab 'geojson' from req.context
            # gather the needed resources
            # create a dictionary in GeoJSON format in 'result' for req.context
            resp.body = req.context['result']
        else:
            raise falcon.HTTPNotFound('The endpoint {name!s} you required'
                                      'does not exist.').format(
                name='/co2/by/' + endpoint
            )

    @falcon.before(max_body(64 * 1024))
    def on_post(self, req, resp):
        """Check if the GeoJSON is in the request"""
        try:
            req.context['geojson']
        except KeyError:
            raise falcon.HTTPBadRequest(
                '"geometry" data missing in request')


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
                'This API only supports responses encoded as JSON.',
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
            req.context['geojson'] = json.loads(body.decode('utf-8'))

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
app.add_route('/co2/by/{endpoint}', class_)
app.add_route('/', hello)

