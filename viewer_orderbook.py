from sys import argv
import signal, os, sys

from dotenv import load_dotenv
load_dotenv()
from dunamu import orderbook, misc

from threading import Thread, RLock
from time import sleep

import pika
from pika.adapters.blocking_connection import BlockingChannel

# https://www.rabbitmq.com/tutorials/tutorial-five-python.html
# https://pika.readthedocs.io/en/stable/modules/channel.html

lock = RLock()
counter = {}

clear = 'cls' if os.name == 'nt' else 'clear'

def main():
    conn = misc.create_pika_connection()
    channel = conn.channel() # type: BlockingChannel

    # 이미 만들어져 있는 exchange의 경우 이름명과 속성이 동일하면 상관없습니다.
    channel.exchange_declare('orderbook', exchange_type='topic')

    # 큐는 굳이 공유될 필요 없음. (topic에서 routing_key에 일치되는 메세지만을 받아옴)
    #
    result = channel.queue_declare('', exclusive=True, auto_delete=True)
    queue_name = result.method.queue # create unique queue!

    # 여러개를 바인딩할수 있습니다.
    channel.queue_bind(exchange='orderbook', queue=queue_name, routing_key="*")


    def callback(ch, method, properties, body):

        market = method.routing_key

        with lock:
            counter.setdefault(market, 0)
            counter[market] += 1

    def monitor():
        while True:

            os.system(clear)

            with lock:

                all = 0
                bases = {}
                bases.setdefault('KRW', 0)
                bases.setdefault('BTC', 0)
                bases.setdefault('ETH', 0)
                bases.setdefault('USDT', 0)

                for key in counter.items():
                    base = key[0].split('-')[0]
                    bases[base] += 1
                    all += 1

                print("Total= %s" % all)
                for key, value in bases.items():
                    sys.stdout.write("%s= %s " % (key, value))
                print("\n")


                for key, value in counter.items():
                    print("%10s -> %02d" % (key, value))

                counter.clear()
            sleep(1)


    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True
    )

    thread = Thread(target=monitor)
    thread.start()

    channel.start_consuming()



if __name__ == '__main__':
    load_dotenv()
    main()