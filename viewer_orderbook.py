from sys import argv
import signal, os

from dotenv import load_dotenv
from dunamu import orderbook, misc



import pika
from pika.adapters.blocking_connection import BlockingChannel

# https://www.rabbitmq.com/tutorials/tutorial-five-python.html
# https://pika.readthedocs.io/en/stable/modules/channel.html

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

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(method) # all about current message!
        # Basic.Deliver ->
        # <Basic.Deliver(['consumer_tag=ctag1.b491f0f260724892867fcc0e338d186e', 'delivery_tag=1', 'exchange=orderbook', 'redelive
        # red=False', 'routing_key=KRW-BTC'])>
        # method.routing_key
        print(" [x] %r:%r" % (method.routing_key, body))

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback)

    channel.start_consuming()



def send():
    conn = misc.create_pika_connection()
    channel = conn.channel()  # type: BlockingChannel

    channel.exchange_declare('orderbook', exchange_type='topic')

    routing_key = 'KRW-BTC'
    message = 'updated!'
    channel.basic_publish(
        exchange='orderbook', routing_key=routing_key, body=message.encode(),
        properties=pika.spec.BasicProperties(delivery_mode=1)
    )
    print(" [x] Sent %r:%r" % (routing_key, message))
    conn.close()


if __name__ == '__main__':
    load_dotenv()

    if len(argv) is 1: main()
    else: send()