import logging
import os

from aiohttp import web
from aiohttp.web import middleware

logger = logging.getLogger(__name__)


@middleware
async def middleware_handle_error(request, handler):
    try:
        resp = await handler(request)
    except web.HTTPException as e:
        return web.json_response({'err': 'http-exception', 'msg': str(e)}, content_type='application/json')
    except Exception as e:
        logger.exception(e)
        return web.json_response({'err': 'server-error', 'msg': 'server error'}, content_type='application/json')
    return resp


INSTALLED_APPS = [
    "account",
    "message",
]
HTTP_LISTEN = '0.0.0.0'
HTTP_PORT = int(os.getenv('HTTP_PORT', '7070'))
MONGODB_ADDR = os.getenv('MONGODB_ADDR', 'mongodb://127.0.0.1:27017/guest_book')
REDIS_ADDR = os.getenv('REDIS_ADDR', 'redis://127.0.0.1:6379/0')
HASH_SALT = '94af841d6732b7bf1354aa753a9bd4faa'
MIDDLEWARES = [
    middleware_handle_error,
]
