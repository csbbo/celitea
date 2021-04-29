import base64
import datetime
import os
import random

import pytz
import hashlib
import settings


def hash_pass(text):
    text = settings.HASH_SALT + text + settings.HASH_SALT
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def b64encode(s):
    b_str = bytes(s, encoding='utf-8')
    b64_b_str = base64.b64encode(b_str)
    return b64_b_str.decode('utf-8')


def b64decode(s):
    b64_b_str = bytes(s, encoding='utf-8')
    b_str = base64.b64decode(b64_b_str)
    return b_str.decode('utf-8')


def utcnow(with_tzinfo=True):
    now = datetime.datetime.utcnow()
    if with_tzinfo:
        return now.replace(tzinfo=datetime.timezone.utc)
    return now


def beijing_now():
    now = utcnow()
    beijing_timezone = pytz.timezone('Asia/Shanghai')
    return now.astimezone(beijing_timezone)


async def save_upload_file(filename, file, path='./'):
    with open(os.path.join(path, filename), 'wb+') as f:
        for chunk in await file.read_chunk():
            f.write(chunk)


def rand_str(length=16, char_type='lower_str'):
    """
    :param length: return str length
    :param char_type: [str, letter, num, hex, lower_str, lower_letter, lower_hex]
    :return: str
    """
    if char_type == 'lower_letter':
        return ''.join(random.choice('qwertyuiopasdfghjklzxcvbnm') for _ in range(length))
    return ''.join(random.choice('1234567890qwertyuiopasdfghjklzxcvbnm') for _ in range(length))
