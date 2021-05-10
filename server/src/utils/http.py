import functools
import hashlib
import json
import logging
import typing

import bson
from aiohttp import web

import settings
from utils import filters, i18n

logger = logging.getLogger(__name__)


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bson.objectid.ObjectId):
            return str(o)
        return json.JSONEncoder.default(o)


def jsondumps(d, **kwargs):
    kwargs['cls'] = Encoder
    return json.dumps(d, **kwargs)


class APIView(web.View):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.request_user = {}
        self.request_data = {}

    @property
    def db(self):
        return self.request.app['db']

    @property
    def redis(self):
        return self.request.app['redis']

    @property
    def sio(self):
        return self.request.app['sio']

    @property
    def i18n(self):
        return i18n.i18n(self.request.headers.get('accept-language'))

    def response(self, data: typing.Union[list, dict, int, float, str], *, status: int = 200):
        return web.json_response(data, content_type='application/json', status=status, dumps=jsondumps)

    def success(self, data: typing.Union[list, dict, int, float, str] = None, *, status: int = 200):
        return self.response({'err': None, 'data': data}, status=status)

    def error(self, msg: str, *, err: str = "error", status: int = 200):
        return self.response({'err': err, 'msg': msg}, status=status)


def get_sid(user):
    text = user['username']
    text += settings.HASH_SALT[::2]
    text += user['password']
    text += settings.HASH_SALT[::5]
    text += str(user.get('logout_time', ''))
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[::2]


def set_sid(uid, sid, response):
    response.set_cookie('uid', uid, max_age=86400 * 2)
    response.set_cookie('sid', sid, max_age=86400 * 2)


async def get_login_user(request) -> dict:
    uid = request.cookies.get('uid')
    sid = request.cookies.get('sid')
    if uid and sid:
        try:
            uid = bson.ObjectId(uid)
            user = await request.app['db'].users.find_one({'_id': uid})
            if user and sid == get_sid(user):
                return user
        except bson.errors.InvalidId:
            pass
    return {}


class check():
    def __init__(self, permission=None, *, login_required=True, validate=None):
        self.permission = permission
        self.login_required = login_required
        self.validate = validate

        if permission and not login_required:
            raise ValueError("invalid check condition")

    def _check_permission(self, user_type):
        if self.permission == '__all__':
            return True

        if isinstance(self.permission, int):
            if user_type >= self.permission:
                return True
        else:
            if user_type in self.permission:
                return True
        return False

    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kw):
            func_self = args[0]
            request = func_self.request

            if self.login_required:
                user = await get_login_user(request)
                if not user:
                    return func_self.error(func_self.i18n.login_required)
                func_self.request_user = user

                if not self._check_permission(user.get('user_type')):
                    return func.error(func_self.i18n.permission_denied)

            if self.validate:
                if request.method == 'GET':
                    request_data = request.rel_url.query
                else:
                    try:
                        request_data = await request.json()
                    except Exception as e:
                        logger.error(str(e))
                        return func_self.error('unknown data type')

                data = filters.validate(self.validate, request_data)
                if not isinstance(data, dict):
                    return func_self.error(data)
                func_self.request_data = data

            return await func(*args, **kw)
        return wrapper
