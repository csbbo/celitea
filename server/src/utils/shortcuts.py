import base64
import datetime
import os
import random
import logging

import pytz
import hashlib
import settings

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import aiosmtplib

logger = logging.getLogger(__name__)


def hash_pass(text):
    text = settings.HASH_SALT + text + settings.HASH_SALT
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def md5_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


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


async def save_file(filename, file, path='./'):
    with open(os.path.join(path, filename), 'wb+') as f:
        for chunk in await file.read_chunk():
            f.write(chunk)


def rand_str(length=16, char_type='lower_str'):
    if char_type == 'lower_letter':
        return ''.join(random.choice('qwertyuiopasdfghjklzxcvbnm') for _ in range(length))
    if char_type == 'number':
        return ''.join(random.choice('1234567890') for _ in range(length))
    return ''.join(random.choice('1234567890qwertyuiopasdfghjklzxcvbnm') for _ in range(length))


async def send_html_email(to_list, subject, html) -> bool:
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    msg = MIMEText(html, 'html', 'utf-8')
    msg['From'] = _format_addr('Celitea <%s>' % settings.EMAIL_SENDER)
    msg['To'] = ';'.join([_format_addr('亲爱的用户 <%s>' % addr) for addr in to_list])
    msg['Subject'] = Header(subject, 'utf-8').encode()

    try:
        async with aiosmtplib.SMTP(hostname=settings.EMAIL_SMTP_SERVER, port=settings.EMAIL_PORT) as smtp:
            await smtp.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
            await smtp.send_message(msg)
        return True
    except aiosmtplib.SMTPException as e:
        logger.error(e)
        return False
