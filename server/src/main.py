#! /usr/bin python3
# -*- encode: utf-8 -*-

import asyncio
import importlib
import inspect
import sys
import logging
from functools import partial

import aioredis
import pymongo
import socketio
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient
from bson.codec_options import CodecOptions

import settings
from utils.http import APIView

logger = logging.getLogger(__name__)


async def setup_app(app):
    for item in settings.INSTALLED_APPS:
        try:
            views = importlib.import_module(item + '.views')
        except ModuleNotFoundError:
            continue
        classes = inspect.getmembers(views, lambda x: inspect.isclass(x) and issubclass(x, APIView) and x.__name__.endswith('API'))
        for name, _class in classes:
            path = '/api/' + name
            app.router.add_route(method='*', path=path, handler=_class)
            logger.info(f'Detected {name}, url: {path}')

    redis = await aioredis.create_redis_pool(settings.REDIS_ADDR)
    app['redis'] = redis

    db = app['db']
    # users
    await db.users.create_index([("username", pymongo.ASCENDING)], unique=True)
    await db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
    await db.users.create_index([("phone", pymongo.ASCENDING)], unique=True)
    await db.users.create_index([("number", pymongo.ASCENDING)], unique=True)


def create_app(loop):
    app = web.Application(middlewares=settings.MIDDLEWARES, client_max_size=(1024 ** 2) * 10)

    db_client = AsyncIOMotorClient(settings.MONGODB_ADDR, serverSelectionTimeoutMS=3000)
    db = db_client.get_database(codec_options=CodecOptions(tz_aware=True))
    app['db'] = db

    sio = socketio.AsyncServer(engineio_logger=False)
    sio.attach(app)
    app['sio'] = sio

    loop.run_until_complete(setup_app(app))
    return app


def main():
    loop = asyncio.get_event_loop()
    logger.error(f'listening http server at {settings.HTTP_LISTEN}:{settings.HTTP_PORT}')
    web.run_app(create_app(loop), host=settings.HTTP_LISTEN, port=settings.HTTP_PORT,
                print=partial(logger.info, color='white', attrs=['bold']), shutdown_timeout=2)
    loop.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
