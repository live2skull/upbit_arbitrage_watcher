'''
! cctx를 사용하면 거래소에 관계없이 동일한 인터페이스로 사용할 수 있음.
-> 프로젝트 1차 작성 / 추후 업그레이드 시 활용할것.
'''

import logging
from requests import Session, get, post
from time import sleep
import parse
import redis

from .misc import get_timestamp, create_logger, create_redis_pool, create_pika_connection
from .config import THROTTLE_API_DEFAULT_TIME, \
    THROTTLE_REMAIN_MIN_TIME ,THROTTLE_REMAIN_SEC_TIME

URL_ORDERBOOK = 'https://api.upbit.com/v1/orderbook'
URL_ALL_MARKET = 'https://api.upbit.com/v1/market/all'


class UpbitAPIClient(Session):

    logger = None
    remainings = {}

    def __init__(self):
        Session.__init__(self)
        self.logger = create_logger('UpbitAPIClient')

    def get(self, group, url, params=None, **kwargs):
        self.check_and_wait(group)
        resp = Session.get(self, url=url, params=params, **kwargs)
        return self.finalize(resp)

    def post(self, group, url, params=None, data=None, **kwargs):
        self.check_and_wait(group)
        resp = Session.post(self, url=url, params=params, data=data, **kwargs)
        return self.finalize(resp)

    def set_initial_remain(self, group):
        self.remainings.setdefault(group, {'min': None, 'sec': None, 'timestamp': None})

    def check_and_wait(self, group, throttle=True):
        # 우선 초 단위의 remain만 핸들링
        self.set_initial_remain(group)
        remain = self.remainings[group]

        # 처음 요청하는 경우 별도로 확인할 필요 없음.
        if remain['timestamp'] is None:
            remain['timestamp'] = get_timestamp()
            return

        # TODO: 스로들링 모듈로 별도 분리?
        # 현재 이전 타임스탬프를 가지고 있음.
        # 현재 타임스탬프와 이전 타임스탬프를 비교해서 계산.
        if throttle:
            tick = get_timestamp() - remain['timestamp'] # 마지막 요청 후 지난 시간
            sl = THROTTLE_API_DEFAULT_TIME - tick

            if sl > 0:
                self.logger.debug("Throttling %s ms" % sl)
                sleep(sl * 0.001) #  millisecond to second

        ## 본 대응법이 오류가 발생하므로 가상 request가 많은 orderbook을 기준으로
        ## 50ms 정도 스토틀링을 추가하였음.
        ## orderobok데이터가 바뀌는 걸 보면 해당 이벤트 발생시마다 바로 반영되는 것이 아니라
        ## 대략 100~200ms 분기별로 데이텨 변경 건이 접수가 되고 있음!
        if remain['min'] is 0:
            self.logger.warn('no remaining in sec! (%s) awaiting %s ms!' % (
                group, THROTTLE_REMAIN_MIN_TIME * 1000
            ))
            while get_timestamp() < remain['timestamp'] + THROTTLE_REMAIN_MIN_TIME:
                sleep(0.05)

        if remain['sec'] is 0:
            self.logger.warn('no remaining in sec! (%s) awaiting %s ms!' % (
                group, THROTTLE_REMAIN_SEC_TIME * 1000
            ))
            while get_timestamp() < remain['timestamp'] + THROTTLE_REMAIN_SEC_TIME:
                sleep(0.05)

    def finalize(self, resp):
        #1. check remaining info!
        _remain_header = resp.headers['Remaining-Req']
        group, min, sec = parse.parse(
            'group={}; min={}; sec={}', _remain_header
        )
        self.set_initial_remain(group)
        remain = self.remainings[group]
        remain['timestamp'] = get_timestamp()
        remain['min'] = int(min)
        remain['sec'] = int(sec)

        self.logger.debug("remaining req: group=%s min=%s sec=%s" % (
            group, min, sec
        ))

        #2. check error info!
        resp_obj = resp.json()
        if type(resp_obj) is dict and 'error' in resp_obj.keys():
            message = resp_obj['error']['message']

            # stack info?
            logging.critical('message: %s' % (
                message
            ))
            raise Exception(message)
        return resp_obj

    #### --- api declaration

    def get_orderbook(self, markets):
        if type(markets) is list:
            markets = ",".join(markets)
        return self.get(group='orderbook', url=URL_ORDERBOOK, params={'markets': markets})


    def get_all_markets(self):
        return self.get(group="market", url=URL_ALL_MARKET)

## TODO: 각 object에 대해 독립적으로 업데이트 등을 작성하여야 함.

REDIS_ALL_MARKETS = ''

class UpbitLocalClient(UpbitAPIClient):
    r = None # type: Redis

    def __init__(self):
        UpbitAPIClient.__init__(self)
        pool = create_redis_pool()
        self.r = redis.StrictRedis(connection_pool=pool)


    def get_all_markets(self, save=True):
        pass



'''
TODO:
class 화 하여 작성 -> Remaning 에 대한 대처가 필요함.
'''

'''
TODO

! gracefully shutdown?
! 한꺼번에 전체 마켓에 대한 정보 로드가 불가능함. 기저통화별로 나누어서 데몬을 구동할 것.

: each function 퍼포먼스 분석 :: static class 작성 중
: 로깅 구체화

: profit 계산식 알고리즘에 따라서 orderbook.units 반환 구성을 파악.  =
: 계산식 사전 정의

'''


def _finalize(resp):
    resp_obj = resp.json()

    if type(resp_obj) is dict and 'error' in resp_obj.keys():
        message = resp_obj['error']['message']

        # stack info?
        logging.critical('message: %s' % (
            message
        ))
        raise Exception(message)

    return resp_obj


def get_orderbook(markets, sess:Session=None):
    _func = get if sess is None else sess.get

    if type(markets) is list:
        markets = ",".join(markets)
    resp = _func(url=URL_ORDERBOOK, params={'markets': markets})

    print(resp.headers)

    return _finalize(resp)


def get_all_market(sess:Session=None):
    _func = get if sess is None else sess.get
    resp = _func(url=URL_ALL_MARKET)

    return _finalize(resp)