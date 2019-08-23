import sys, os
import redis

from dunamu import apis, misc

def get_market_list(market_base: str):

    pool = misc.create_redis_pool()
    r = redis.StrictRedis(connection_pool=pool)

    res = []
    markets = apis.get_all_market()
    for market in markets:
        m = market['market']
        if m.split('-')[0] == market_base:
            res.append(m)

    r.lpush(apis.MARKETS_ALL, *res)
    print(','.join(res))






def main():
    func = sys.argv[1]

    if func == 'market_list':
        get_market_list(sys.argv[2])


if __name__ == '__main__':
    main()