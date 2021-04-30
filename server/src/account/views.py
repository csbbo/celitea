import logging
import os
import time

import pymongo

import settings
from account.validate import *
from utils.http import APIView, check, get_sid, set_sid
from utils.shortcuts import hash_pass, rand_str, send_html_email, save_file

logger = logging.getLogger(__name__)


class EmailCaptchaAPI(APIView):
    @check(login_required=False, validate=EmailCaptchaValidator)
    async def post(self):
        email = self.request_data['email']
        captcha = await self.redis.get(f'{email}email_captcha')
        if captcha:
            return self.error(self.i18n.email_already_send)

        captcha = rand_str(length=4, char_type='number')
        html = f"<h2>{captcha}</h2>"
        is_success = await send_html_email([email, ], self.i18n.celitea_email_captcha, html)
        if not is_success:
            return self.error(self.i18n.email_send_error)

        await self.redis.set(f'{email}_captcha', captcha, expire=60)
        return self.success()


class RegisterAPI(APIView):
    @check(login_required=False, validate=RegisterValidator)
    async def post(self):
        data = self.request_data
        captcha = await self.redis.get(f"{data['email']}_captcha")
        if not captcha or str(captcha, encoding='utf-8') != data['captcha']:
            return self.error(self.i18n.captcha_error)

        if await self.db.users.find_one({'username': data['username']}):
            return self.error(self.i18n.user_exists)
        if await self.db.users.find_one({'email': data['email']}):
            return self.error(self.i18n.email_exists)

        timestamp = time.time()
        try:
            await self.db.users.insert_one({
                'username': data['username'],
                'password': hash_pass(data['password']),
                'email': data['email'],
                'create_time': timestamp,
                'update_time': timestamp
            })
        except pymongo.errors.DuplicateKeyError:
            return self.error(self.i18n.user_exists)
        except Exception as e:
            logger.exception(e)
            return self.error(self.i18n.server_error)
        return self.success()


class LoginAPI(APIView):
    @check(login_required=False, validate=LoginValidator)
    async def post(self):
        data = self.request_data
        user = await self.db.users.find_one({'username': data['username']})
        if not user:
            return self.error(self.i18n.user_not_exists)
        if hash_pass(data['password']) != user.get('password'):
            return self.error(self.i18n.password_error)

        await self.db.users.update_one({'_id': user['_id']}, {'$set': {'login_time': time.time()}})
        sid = get_sid(user)
        response = self.success()
        set_sid(str(user['_id']), sid, response)
        return response


class LogoutAPI(APIView):
    @check(permission='__all__')
    async def post(self):
        user = self.request_user
        await self.db.users.update_one({'_id': user['_id']}, {'$set': {'logout_time': time.time()}})
        return self.success()


class UploadAvatarAPI(APIView):
    @check(permission='__all__')
    async def post(self):
        data = await self.request.post()
        file_obj = data['file']

        save_name = str(self.request_user['_id'])
        await save_file(save_name, file_obj.file, path=settings.AVATAR_PATH)
        return self.success(data={'path': os.path.join(settings.AVATAR_PATH, save_name)})


class ProfileAPI(APIView):
    @check(permission='__all__')
    async def get(self):
        user = self.request_user
        data = {
            'username': user['username'],

            'email': user.get('email'),
            'phone': user.get('phone'),
            'remark': user.get('remark'),
            'avatar': user.get('avatar'),
            'user_type': user.get('user_type'),

            'number': user.get('number'),
            'sex': user.get('sex'),
            'wechat': user.get('wechat'),
            'qq': user.get('qq'),
            'github': user.get('github'),
            'blog': user.get('blog'),
            'birthday': user.get('birthday'),
            'grade': user.get('grade'),
            'major': user.get('major'),
            'company': user.get('company'),
            'location': user.get('location'),

            'login_time': user.get('login_time'),
        }
        return self.success(data)

    @check(permission='__all__', validate=ProfilePostValidator)
    async def post(self):
        user = self.request_user
        return self.success(user)
