import bson
from multidict._multidict import MultiDictProxy


def validate(dic, data):
    parse_data = {}
    if isinstance(data, MultiDictProxy):
        for k in data:
            if k not in dic:
                continue
            parse_data[k] = data.getall(k) if k in parse_data else data.get(k)
    else:
        for k, v in data.items():
            if k not in dic:
                continue
            parse_data[k] = v

    for key, funcs in dic.items():
        for f in funcs:
            if err := f(key, parse_data):
                return err
    return parse_data


def required(key, data):
    if key not in data:
        return f'{key} is required'


def not_empty(key, data):
    if key not in data:
        return ''
    if bool(data[key]) is False:
        return f'{key} can not be empty'


def objectid(key, data):
    if key not in data:
        return ''
    try:
        bson.ObjectId(data.get(key))
    except bson.errors.InvalidId:
        return f'{key} is not invalid ObjectId'


def type_int(key, data):
    if key not in data:
        return ''
    if not isinstance(data[key], int):
        return f'{key} is not int'


def type_list(key, data):
    if key not in data:
        return ''
    if not isinstance(data[key], list):
        return f'{key} is not list'


def type_dict(key, data):
    if key not in data:
        return ''
    if not isinstance(data[key], dict):
        return f'{key} is not dict'


objectid_validator = {
    'id': [required, objectid]
}
