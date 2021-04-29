import logging

import pymongo

from account.validate import *
from utils.http import APIView, check, get_sid, set_sid
from utils.shortcuts import hash_pass, rand_str

logger = logging.getLogger(__name__)


class RegisterAPI(APIView):
    @check(login_required=False, validate=register_validator)
    async def post(self):
        data = self.request_data

        try:
            insert_result = await self.db.users.insert_one({
                'username': data['username'],
                'password': hash_pass(data['password']),
                'secret': rand_str(),
            })
        except pymongo.errors.DuplicateKeyError:
            return self.error(self.i18n.user_exists)
        except Exception as e:
            logger.exception(e)
            return self.error(self.i18n.server_error)

        uid = insert_result.inserted_id
        return self.success({'uid': str(uid)})


class LoginAPI(APIView):
    @check(login_required=False, validate=login_validator)
    async def post(self):
        data = self.request_data

        user = await self.db.users.find_one({'username': data['username']})
        if not user:
            return self.error(self.i18n.user_not_exists)
        if hash_pass(data['password']) != user.get('password'):
            return self.error(self.i18n.password_error)

        sid = get_sid(user)
        response = self.success()
        set_sid(str(user['_id']), sid, response)
        return response


class LogoutAPI(APIView):
    @check(login_required=True)
    async def post(self):
        user = self.request_user
        update_result = await self.db.users.update_one({'_id': user['_id']}, {'$set': {'secret': rand_str()}})
        if not update_result.modified_count:
            return self.error(self.i18n.server_error)
        return self.success()


class UserAPI(APIView):
    @check(login_required=True)
    async def get(self):
        return self.success(self.request_user)
