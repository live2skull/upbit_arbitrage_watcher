import os, sys
import redis


from dotenv import load_dotenv
from dunamu import apis, misc


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
    load_dotenv()
    func = sys.argv[1]

    if func == 'verify_orderbook':
        verify_orderbook()
    elif func == 'pika_recv':
        pika_recv()
    elif func == 'pika_send':
        pika_send()

if __name__ == '__main__':
    main()