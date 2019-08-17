import time
import redis
import os
from requests import Session



def get_timestamp():
    # 1566020586537
    # 1565988623993
    # pre, flt = str(time.time()).split('.')

    return int(time.time() * 1000)


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
