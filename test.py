from dotenv import load_dotenv
load_dotenv()

import os, sys
import redis

from dunamu import apis, misc, calculator


def calc():
    pool = misc.create_redis_pool()
    r = redis.StrictRedis(connection_pool=pool)

    ask_prices = r.lrange('KRW-BTC_orderbook_ask_prices', 0, -1)
    ask_amounts = r.lrange('KRW-BTC_orderbook_ask_amounts', 0, -1)
    bid_prices = r.lrange('KRW-BTC_orderbook_bid_prices', 0, -1)
    bid_amounts = r.lrange('KRW-BTC_orderbook_bid_amounts', 0, -1)

    print(ask_prices, ask_amounts, bid_prices, bid_amounts)



def verify_orderbook():
    pool = misc.create_redis_pool()
    r = redis.StrictRedis(connection_pool=pool)

    err = []

    keys = r.keys('*_last_*')
    for k in keys:
        k = k.decode()
        val = int(r.get(k).decode())
        if val is not 0:
            print('%s is %s : OK!' % (k, val))
        else:
            err.append(k)

    print(" ".join(err))


def pika_send():
    connection = misc.create_pika_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange='orderbook', exchange_type='topic')

    message = ' '.join(sys.argv[1:]) or "info: Hello World!"
    channel.basic_publish(exchange='orderbook', routing_key='', body=message)
    print(" [x] Sent %r" % message)
    connection.close()


def pika_recv():
    pass


def main():
    func = sys.argv[1]

    if func == 'verify_orderbook':
        verify_orderbook()
    elif func == 'pika_recv':
        pika_recv()
    elif func == 'pika_send':
        pika_send()
    elif func == 'calc':
        calc()

if __name__ == '__main__':
    main()