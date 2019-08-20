from dotenv import load_dotenv
load_dotenv()

import os, sys
import redis

from dunamu import apis, misc, calculator, orderbook
from dunamu.orderbook import ASK_AMOUNTS, ASK_PRICES,\
    BID_AMOUNTS, BID_PRICES, LAST_REQUEST_TIME, LAST_UPDATE_TIME


# https://datascienceschool.net/view-notebook/148fc57f684c4dc48eeb5048ab0d45f2/

def calc():

    order = orderbook.Orderbook('KRW-BTC')
    units = order.units

    # 잘 돌아가는것 같기도....
    balance, amount = calculator.vt_buy_all(13500000, 0.05, units[ASK_PRICES], units[ASK_AMOUNTS])
    print(balance, amount)


    balance, amount = calculator.vt_sell_all(0.23510001, 0.05, units[BID_PRICES], units[BID_AMOUNTS])
    print(balance, amount)


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