'''
! cctx를 사용하면 거래소에 관계없이 동일한 인터페이스로 사용할 수 있음.
-> 프로젝트 1차 작성 / 추후 업그레이드 시 활용할것.
'''

import logging
from requests import Session, get, post
from time import sleep
import parse

from .misc import get_timestamp

URL_ORDERBOOK = 'https://api.upbit.com/v1/orderbook'
URL_ALL_MARKET = 'https://api.upbit.com/v1/market/all'


class UpbitAPIClient(Session):

    remainings = {}

    def __init__(self):
        Session.__init__(self)

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

    def check_and_wait(self, group):
        # 우선 초 단위의 remain만 핸들링
        self.set_initial_remain(group)
        remain = self.remainings[group]

        # 처음 요청하는 경우 별도로 확인할 필요 없음.
        if remain['timestamp'] is None:
            remain['timestamp'] = get_timestamp()
            return

        elif remain['sec'] is 0:
            # 남은 remaining 이 없는 경우 일정 시간 대기하면서 기다린다.
            while get_timestamp() < remain['timestamp'] + 1000:
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
        return self.get(group='market', url=URL_ORDERBOOK, params={'markets': markets})


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