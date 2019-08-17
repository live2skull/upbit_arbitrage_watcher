'''
! cctx를 사용하면 거래소에 관계없이 동일한 인터페이스로 사용할 수 있음.
-> 프로젝트 1차 작성 / 추후 업그레이드 시 활용할것.
'''

import logging
from requests import Session, get, post

URL_ORDERBOOK = 'https://api.upbit.com/v1/orderbook'
URL_ALL_MARKET = 'https://api.upbit.com/v1/market/all'


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
        logging.critical('\nmessage: %s' % (
            message
        ))
        raise Exception(message)

    return resp_obj


def get_orderbook(markets, sess:Session=None):
    _func = get if sess is None else sess.get

    if type(markets) is list:
        markets = ",".join(markets)
    resp = _func(url=URL_ORDERBOOK, params={'markets': markets})

    return _finalize(resp)


def get_all_market(sess:Session=None):
    _func = get if sess is None else sess.get
    resp = _func(url=URL_ALL_MARKET)

    return _finalize(resp)