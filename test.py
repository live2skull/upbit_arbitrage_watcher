import os, sys
import redis

from dotenv import load_dotenv
from dunamu import apis, misc


def verify_orderbook():
    pool = misc.create_redis_pool()
    r = redis.StrictRedis(connection_pool=pool)

    keys = r.keys('*_last_*')
    for k in keys:
        k = k.decode()
        val = int(r.get(k).decode())
        if val is not 0:
            print('%s is %s : OK!' % (k, val))
        else:
            raise Exception('%s value is not set' % k)

def main():
    load_dotenv()
    func = sys.argv[1]

    if func == 'verify_orderbook':
        verify_orderbook()

if __name__ == '__main__':
    main()