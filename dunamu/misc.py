import time
import logging
import os, sys

import pika
import redis
from requests import Session

from .config import LOGGING_FORMAT, LOGGING_LEVEL


def get_timestamp():
    # 1566020586537
    # 1565988623993
    # pre, flt = str(time.time()).split('.')

    return int(time.time() * 1000)


def create_logger(name: str, level:int = LOGGING_LEVEL, format:str = LOGGING_FORMAT,
                  propagate=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate

    formatter = logging.Formatter(format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def create_pika_connection(host=None, port=None, user=None, password=None,
                           virtual_host=None):
    host = host if host else os.getenv('PIKA_HOST', None)
    port = port if port else os.getenv('PIKA_PORT', None)
    user = user if user else os.getenv('PIKA_USER', None)
    password = password if password else os.getenv('PIKA_PASSWORD', None)
    virtual_host = virtual_host if virtual_host else os.getenv('PIKA_VIRTUAL_HOST', None)

    conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host, port=port, virtual_host=virtual_host,
            credentials=pika.PlainCredentials(user, password),
        )
    )
    return conn


def create_redis_pool(host=None, port=None, db=None):
    host = host if host else os.getenv('REDIS_HOST', None)
    port = port if port else os.getenv('REDIS_PORT', None)
    db = db if db else os.getenv('REDIS_DB', db)

    return redis.ConnectionPool(host=host, port=port, db=db)


def create_web_session():
    sess = Session()
    del sess.headers['User-Agent']

    return sess



class PerformanceCounter:
    name = "Example"

    @staticmethod
    def static():
        print ("s static() called")
