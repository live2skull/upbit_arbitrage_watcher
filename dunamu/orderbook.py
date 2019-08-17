from sys import argv, stdout
import signal, os

import logging
from threading import Thread

from requests import Session
import redis

from dotenv import load_dotenv

from .config import TIMEOUT_REDIS_LOCK, LOGGING_LEVEL, LOGGING_FORMAT

from .apis import UpbitAPIClient
from .misc import create_web_session, create_redis_pool, get_timestamp


# KRW-BTC_orderbook__lock

# https://redis.io/commands/rpush -> documentation!
# https://www.joinc.co.kr/w/man/12/REDIS/IntroDataType
# https://docs.python.org/2/library/timeit.html | performance checking

ASK_PRICES = '_ask_prices'
ASK_SIZES = '_ask_sizes'
BID_PRICES = '_bid_prices'
BID_SIZES = '_bid_sizes'

LAST_UPDATE_TIME = '_last_update_time'
LAST_REQUEST_TIME = '_last_request_time'


class Orderbook:

    logger = None
    r = None  # type: redis.Redis

    # ex) KRW-BTC_orderbook
    r_name = ""  # type: str
    # ex) KRW-BTC_orderbook__lock
    r_lock = ""  # type: str
    r_lock_obj = None

    market = None  # type: str

    last_update_time = None  # type: long
    last_request_time = None  # type: long

    @property
    def units(self):
        with self.r_lock_obj:
            pass
            # 데이터 4개를 가져와서 반환한다.
            # 이렇게 작성해 놓으면 orderbook 객체는 orderbook 데몬에서 동작
            # -> 실시간으로 업데이트된 값을 저장한다.
            # 추가로 calculator 에서 필요할 때마다 데이터를 불러와서 사용.

            # return self.r.hgetall(self.r_name)

    def _update_timestamp(self):
        self.r.set(self.r_name + LAST_REQUEST_TIME, self.last_request_time)
        self.r.set(self.r_name + LAST_UPDATE_TIME, self.last_update_time)

    def _update_orderbook(self, units):
        self.r.delete(self.r_name + ASK_PRICES)
        self.r.delete(self.r_name + ASK_SIZES)
        self.r.delete(self.r_name + BID_PRICES)
        self.r.delete(self.r_name + BID_SIZES)

        bid_prices = []; bid_sizes = []
        ask_prices = []; ask_sizes = []

        for u in units:
            bid_prices.append(u['bid_price'])
            bid_sizes.append(u['bid_size'])
            ask_prices.append(u['ask_price'])
            ask_sizes.append(u['ask_size'])

        self.r.rpush(self.r_name + ASK_PRICES, *ask_prices)
        self.r.rpush(self.r_name + ASK_SIZES, *ask_sizes)
        self.r.rpush(self.r_name + BID_PRICES, *bid_prices)
        self.r.rpush(self.r_name + BID_SIZES, *bid_sizes)

    def update(self, timestamp, units):
        self.last_request_time = get_timestamp()

        if timestamp <= self.last_update_time:
            # last_request_time 은 별도로 접근할때 충돌 위험이 크지 않으므로 별도로 lock하지 않습니다.
            self.r.set(self.r_name + LAST_REQUEST_TIME, self.last_request_time)
            # with self.r.lock(self.r_lock, blocking_timeout=TIMEOUT_REDIS_LOCK) as lock:
            #     self._update_timestamp()
            return False

        else:
            with self.r_lock_obj:
                self._update_timestamp()
                self._update_orderbook(units)

            ## TODO: add initialized flag
            if self.last_update_time is 0:
                # 초기화 동작은 업데이트로 전파하지 않음.
                self.last_update_time = timestamp
                return False
            else:
                self.last_update_time = timestamp
                self.logger.debug('orderbook updated.')
                return True

    ## support *redis* memory sharing!
    def __init__(self, market: str, pool):
        self.market = market
        self.last_request_time = 0
        self.last_update_time = 0


        self.r_name = "%s_orderbook" % self.market
        self.r_lock = "%s__lock" % self.r_name
        self.r = redis.Redis(connection_pool=pool)
        self.r_lock_obj = self.r.lock(self.r_lock, blocking_timeout=TIMEOUT_REDIS_LOCK)
        self.r.delete(self.r_lock)

        self.logger = logging.getLogger(self.r_name)
        self.logger.setLevel(LOGGING_LEVEL)
        self.logger.propagate = False # root 핸들러에 전달하지 않음??

        formatter = logging.Formatter(LOGGING_FORMAT)
        stream_hander = logging.StreamHandler(stdout)
        stream_hander.setFormatter(formatter)
        self.logger.addHandler(stream_hander)




class OrderbookDaemon(Thread):
    logger = None

    is_running = None  # type: bool
    client = None # type: UpbitAPIClient
    pool = None  # type: redis.ConnectionPool

    market_base = None # type: str
    markets = None # type: dict
    markets_str = None # type: str

    def __init__(self, market_base:str, markets: str):
        ## TODO: 데몬이 사전에 실행되고 있는가?

        Thread.__init__(self)
        self.is_running = False
        self.markets_str = markets
        self.market_base = market_base
        self.markets = dict()

        self.client = UpbitAPIClient()
        self.pool = create_redis_pool()

        # initializing orderbook
        # def __init__(self, market: str, pool):
        # 이렇게 하면 각각의 orderbook 객체별로 하나의 커넥션을 이용해 redis를 이용할 수 있습니다.
        for market in markets.split(','):
            self.markets.setdefault(market, Orderbook(market, self.pool))


        # 로깅 옵션을 설정합니다.
        self.logger = logging.getLogger("%s_orderbook_daemon" % self.market_base)
        self.logger.setLevel(LOGGING_LEVEL)
        self.logger.propagate = False  # root 핸들러에 전달하지 않음??

        formatter = logging.Formatter(LOGGING_FORMAT)
        stream_hander = logging.StreamHandler(stdout)
        stream_hander.setFormatter(formatter)
        self.logger.addHandler(stream_hander)


    # overwrite
    def run(self):
        self.logger.info("%s 마켓 호가 데몬이 시작되었습니다. (총 %s개 로드)" % (
            self.market_base, len(self.markets)
        ))

        self.is_running = True
        self.loop()

    # overwrite
    def join(self, timeout=None):
        self.is_running = False
        Thread.join(self, timeout)

    def loop(self):
        while self.is_running:
            resp = self.client.get_orderbook(self.markets_str)

            for ifo in resp:
                market = ifo['market']
                timestamp = ifo['timestamp']
                units = ifo['orderbook_units']

                updated = self.markets[market].update(timestamp, units)

            # market 별로 데이터 추출해서 orderbook에 넣어줍니다.

    def send_update_event(self, market):
        # TODO: using rabbitmq messenger!
        pass
