import importlib
import inspect
import json
import logging
import multiprocessing
import os
import time

import pymongo
import requests

import main
import settings
from utils.http import get_sid
from utils.shortcuts import hash_pass

logger = logging.getLogger(__name__)


HTTP_PORT = settings.HTTP_PORT + 1
MONGODB_ADDR = settings.MONGODB_ADDR + '_test'


def pprint(s, color='none', background=False, output=True):
    clr_lst = ['white', 'red', 'light_yellow', 'yellow', 'blue', 'purple', 'cyan', 'grey', 'light_grey']
    if color in clr_lst:
        index = str(clr_lst.index(color))
        num = '4' + index if background else '3' + index
        s = f'\033[1;{num}m{s}\033[0m'
    if output:
        print(s)
    return s


class TestCase:
    def __init__(self):
        self.login = True
        self.uid = '',
        self.sid = '',
        self.user = {}
        self.url = ''

    @property
    def db(self):
        db_client = pymongo.MongoClient(MONGODB_ADDR.rsplit('/', 1)[0])
        db = db_client[MONGODB_ADDR.rsplit('/', 1)[1]]
        return db

    def create_user(self, test_username='test_admin', test_password='test_admin', login=True):
        insert_user = {'username': test_username, 'password': hash_pass(test_password)}
        insert_result = self.db.users.insert_one(insert_user)
        insert_user['_id'] = insert_result.inserted_id
        uid = str(insert_user['_id'])
        sid = get_sid(insert_user)

        if login is False:
            self.login = False
        self.uid, self.sid = uid, sid
        return insert_user

    def get_url(self, url):
        return f'http://127.0.0.1:{HTTP_PORT}/api/{url}'

    def clear_db(self):
        db_client = pymongo.MongoClient(MONGODB_ADDR.rsplit('/', 1)[0])
        db_client.drop_database(MONGODB_ADDR.rsplit('/', 1)[1])

    def assert_success(self, resp):
        if resp['err'] is not None:
            pprint(resp['msg'], color='red')
            return False
        return True

    def assert_failed(self, resp):
        if resp['err'] is None:
            pprint('expect fail but success', color='red')
            return False
        return True

    def get(self, *args, **kw):
        if self.login:
            if 'headers' not in kw:
                kw['headers'] = {}
            kw['headers']['cookie'] = f'uid={self.uid}; sid={self.sid};'

        # if kw.get('data'):
        #     kw['data'] = json.dumps(kw['data'])

        return requests.get(*args, **kw)

    def post(self, *args, **kw):
        if self.login:
            if 'headers' not in kw:
                kw['headers'] = {}
            kw['headers']['cookie'] = f'uid={self.uid}; sid={self.sid};'
        if kw.get('data'):
            kw['data'] = json.dumps(kw['data'])

        return requests.post(*args, **kw)

    def put(self, *args, **kw):
        if self.login:
            if 'headers' not in kw:
                kw['headers'] = {}
            kw['headers']['cookie'] = f'uid={self.uid}; sid={self.sid};'
        if kw.get('data'):
            kw['data'] = json.dumps(kw['data'])

        return requests.put(*args, **kw)

    def delete(self, *args, **kw):
        if self.login:
            if 'headers' not in kw:
                kw['headers'] = {}
            kw['headers']['cookie'] = f'uid={self.uid}; sid={self.sid};'
        if kw.get('data'):
            kw['data'] = json.dumps(kw['data'])

        return requests.delete(*args, **kw)


def detection_and_run_test():
    all_test_count = 0
    fail_test_count = 0
    start_time = time.time()
    for item in settings.INSTALLED_APPS:
        try:
            tests = importlib.import_module(item + '.tests')
        except ModuleNotFoundError:
            continue
        pprint(f'\n[modul {item}]', color='light_yellow')
        classes = inspect.getmembers(tests, lambda x: inspect.isclass(x) and x.__name__.endswith('APITest'))
        classes.reverse()
        for name, _class in classes:
            pprint(f'[Test Class: {name}]', color='yellow')
            test_func_list = list(filter(lambda x: x.endswith('_test'), dir(_class)))
            test_func_list.reverse()
            obj = _class()
            try:
                obj.setup()
                for test_func in test_func_list:
                    is_success = getattr(obj, test_func)()
                    if not is_success:
                        fail_test_count += 1
                        break
            except Exception as e:
                logger.exception(e)
            finally:
                all_test_count += 1

    pprint(f'\nRan {all_test_count} tests in {round(time.time()-start_time, 2)}s')
    if not fail_test_count:
        pprint('OK')
    else:
        pprint(f'FAILED (failures={fail_test_count})')


if __name__ == '__main__':
    # run test server
    os.environ['HTTP_PORT'] = str(HTTP_PORT)
    os.environ['MONGODB_ADDR'] = MONGODB_ADDR
    p1 = multiprocessing.Process(target=main.main)
    p1.start()
    pprint(f'Running test server on {settings.HTTP_LISTEN}:{HTTP_PORT}')
    db_name = MONGODB_ADDR.rsplit('/', 1)[1]
    pprint(f'Create test database {db_name}')
    time.sleep(0.5)

    # run unit test
    try:
        detection_and_run_test()
    finally:
        db_client = pymongo.MongoClient(MONGODB_ADDR.rsplit('/', 1)[0])
        db_client.drop_database(MONGODB_ADDR.rsplit('/', 1)[1])
        pprint(f'Drop test database {db_name}')
        p1.terminate()
