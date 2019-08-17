from sys import argv
import signal, os

from dotenv import load_dotenv
from dunamu import orderbook



# TODO: add signal detection -> stop daemon gracefully (lock 오류방지 및 데이터 flush)
# TODO: orderbook daemon 로거 설정


def main():
    load_dotenv()

    market_base = argv[1]
    markets = argv[2] # TODO: replace markets arg -> markets file
    # 옵션 파싱기를 사용하자.

    def signal_handler(sig, frame):
        print("!!! ** warm shutdown. please wait... ")
        daemon.join(timeout=5)
        print("!!! now exit.")
        exit(0)


    # 윈도우에서 제대로 동작하지 않는 것 같음.
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGKILL, signal_handler)  # support windows pycharm environment


    daemon = orderbook.OrderbookDaemon(market_base, markets)
    daemon.start()



    while True:
        input()




if __name__ == '__main__':
    main()