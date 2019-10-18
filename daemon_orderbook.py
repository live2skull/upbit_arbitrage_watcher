from sys import argv
import signal, os

from dotenv import load_dotenv
load_dotenv()
from dunamu import orderbook
from dunamu import apis

# TODO: add signal detection -> stop daemon gracefully (lock 오류방지 및 데이터 flush)
# TODO: orderbook daemon 로거 설정


def main():

    daemons = []

    # TODO: add option parser
    market_bases = argv[1].upper().split(',') # type: str
    _markets = apis.UpbitLocalClient().all_markets


    def signal_handler(sig, frame):
        print("!!! ** warm shutdown. please wait... ")
        for _daemon in daemons: # type: orderbook.OrderbookDaemon
            _daemon.join(timeout=5)
        print("!!! now exit.")
        exit(0)


    # 윈도우에서 제대로 동작하지 않는 것 같음.
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGKILL, signal_handler)  # support windows pycharm environment


    for market_base in market_bases:
        # result = list(filter(lambda x: (x % 13 == 0), my_list))
        # lambda + map 이용할 경우 None 값이 리스트에 포함되면 안된다.
        # filter 이용하여 True 반환되는 값만 이용한다.
        markets = list(filter(lambda x: x.split('-')[0] == market_base, _markets))
        daemon = orderbook.OrderbookDaemon(market_base, markets)
        daemons.append(daemon)

    for daemon in daemons:
        daemon.start()

    while True:
        input()



if __name__ == '__main__':
    main()