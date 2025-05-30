import json
import logging

from tornado.web import HTTPError
from rest_tools.server import (
    RestHandler,
    RestHandlerSetup,
    RestServer,
)

from . import __version__ as version
from .config import ENV
from .group_validation import Validator


logger = logging.getLogger('server')


class BaseHandler(RestHandler):
    def initialize(self, validate=None, **kwargs):
        self.validate = validate
        return super().initialize(**kwargs)

    def get_current_user(self):
        try:
            type, val = self.request.headers['Authorization'].split(' ', 1)
            if type.lower() != 'bearer':
                raise Exception('bad header type')
            logger.debug('Authorization: bearer %r', val)
            if val == ENV.AUTH_SECRET:
                return 'valid'
            else:
                logger.info('invalid authorization!')
        # Auth Failed
        except Exception:
            if self.debug and 'Authorization' in self.request.headers:
                logger.info('Authorization: %r', self.request.headers['Authorization'])

        return None


class Main(BaseHandler):
    def get(self):
        self.write({})


class Auth(BaseHandler):
    def post(self):
        logging.debug('request headers: %r', dict(self.request.headers))
        if not self.current_user:
            raise HTTPError(401, 'not authorized')
        logging.debug('current_user: %r', self.current_user)

        logging.debug('request body: %r', self.request.body)
        data = json.loads(self.request.body)
        logging.info('request for %r', data)

        scopes = ''
        try:
            username = data['username']
            requested_scopes = [x for x in data['scopes'].split() if x.startswith('storage.')]
            if requested_scopes:
                potential_scopes = []
                for s in requested_scopes:
                    if self.validate(username=username, scope=s):
                        potential_scopes.append(s)
                scopes = ' '.join(potential_scopes)
                logging.debug('valid scopes: %s', scopes)
            else:
                # default case
                scopes = f'storage.read:/data/user/{username} storage.modify:/data/user/{username}'
        except Exception:
            logging.info('failed to get scopes', exc_info=True)
            raise HTTPError(400, 'invalid scopes')

        self.write({
            'scopes': scopes,
        })


class Health(BaseHandler):
    async def get(self):
        ret = {}
        try:
            self.validate.base_path.exists()
        except Exception:
            self.set_status(500)
            ret['base_path'] = False
        self.write(ret)


class Server:
    def __init__(self):
        if not ENV.AUTH_SECRET:
            raise RuntimeError('Must define an AUTH_SECRET')

        handler_config = {
            'debug': ENV.DEBUG,
            'server_header': f'OAuth2 Proxy {version}',
        }
        kwargs = RestHandlerSetup(handler_config)
        kwargs['route_stats'] = None  # disable route stats for more speed
        kwargs['validate'] = Validator(ENV.BASE_PATH)

        server = RestServer(
            debug=ENV.DEBUG,
        )

        server.add_route('/', Main, kwargs)
        server.add_route('/auth', Auth, kwargs)
        server.add_route('/healthz', Health, kwargs)

        server.startup(address=ENV.HOST, port=ENV.PORT)

        self.server = server

    async def start(self):
        pass

    async def stop(self):
        await self.server.stop()
