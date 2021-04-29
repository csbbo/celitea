import bson
from multidict._multidict import MultiDictProxy
import re


def validate(validator, data):
    """
    :param validator: validator
    :param data: request data
    :return: request data after parsing or error string
    """
    ret = {}
    if isinstance(data, MultiDictProxy):    # GET请求数据
        for key in data:
            ret[key] = data.getall(key) if key in ret else data.get(key)
        data = ret
    for key, func_list in validator.items():
        item = data.get(key)
        if not_required in func_list:
            func_list.remove(not_required)
        elif item is None:
            return f'{key} is required'

        item.strip()
        if allow_empty in func_list:
            func_list.remove(allow_empty)
        elif item == '':
            return f'{key} can not be empty'

        if item:
            for f in func_list:
                if err := f(key, item):
                    return err
    return data


not_required = 'not_required'
allow_empty = 'allow_empty'


def object_id(key, content):
    try:
        bson.ObjectId(content)
    except bson.errors.InvalidId:
        return f'{key} is not invalid ObjectId'


def type_int(key, content):
    if not isinstance(content, int):
        return f'{key} is not int'


def type_list(key, content):
    if not isinstance(content, list):
        return f'{key} is not list'


def type_dict(key, content):
    if not isinstance(content, dict):
        return f'{key} is not dict'


def email(key, content):
    reg_exp = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    if not re.match(reg_exp, content):
        return f'{key} is not a valid email'


def phone(key, content):
    reg_exp = r'^1(3[0-9]|4[5,7]|5[0,1,2,3,5,6,7,8,9]|6[2,5,6,7]|7[0,1,7,8]|8[0-9]|9[1,8,9])\d{8}$'
    if not re.match(reg_exp, content):
        return f'{key} is not a valid phone'


ObjectIdValidator = {
    'id': [object_id]
}
