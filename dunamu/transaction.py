
from copy import copy

from .apis import UpbitLocalClient
from .calculator import vt_buy_all, vt_sell_all
from .orderbook import Orderbook, BID_AMOUNTS, BID_PRICES, ASK_AMOUNTS, ASK_PRICES
from .misc import create_redis_pool, create_logger

# 오더북 캐싱 부분 (각 객체는 단일 스레드에서 사용될 것이므로, 이렇게 해도 상관없습니다.
_upbitLocalClient = UpbitLocalClient()
_orderbooks = {}

_redis_connection_pool = None

# 본래 필요한 마켓들만 캐싱하면 되지만...
# TODO: 시운전을 위해 이부분은 추후 별도로 최적화합니다.
def _init_local_options():
    _redis_connection_pool = create_redis_pool()

    for market in _upbitLocalClient.get_all_markets():
        _orderbooks.setdefault(market, Orderbook(market, pool=_redis_connection_pool))


_init_local_options()
_fee = _upbitLocalClient.fee
_coin_bases = _upbitLocalClient.base_markets

def _get_orderbook(market):
    return _orderbooks[market]


## 전체 마켓 코인리스트를 가져와서 ["":""] 쌍으로 설정

class Wallet:

    account = None # type: dict

    def update(self, wallet):
        self.account.clear()
        for k,v in wallet.account.items():
            self.account.setdefault(k, v)

    def set(self, coin, amount):
        self.account.setdefault(coin, float(amount))
        self.account[coin] = float(amount)

    def get(self, coin):
        if coin not in self.account.keys():
            self.account.setdefault(coin, float(0))

        return self.account[coin]

    def __init__(self):
        self.account = dict()


TRX_BUY = 0
TRX_SELL = 1


# TODO: logger service Object inheritance support?
# virtual transaction implementation!


'''
현재 정보: 거래 이후의 상태 반환.

'''

class Transaction:

    # cached!
    orderbook = None # type: orderbook

    logger = None

    market = None # type: str
    coin_base = None # type: str
    coin_target = None # type: str
    fee = None # type: float

    wallet = None # type: Wallet
    transaction_type = None # type: int

    front = None # type: Transaction
    nexts = None # type: list

    @property
    def is_start(self):
        return self.front is None

    @property
    def is_terminal(self):
        return len(self.nexts) is 0

    @property
    def coin_current(self):
        # 정확한 기준이...? ex) KRW-BTC -> 거래 이후의 상태를 반환합니다.
        # self.transaction_type == TRX_BUY : self.coin_current
        # self.transaction_type == TRX_SELL: self.coin_target
        return self.coin_base if self.transaction_type is TRX_SELL else self.coin_target

    @property
    def coin_is_base(self):
        return self.coin_current in _coin_bases

    def __init__(self, market, transaction_type, front=None):
        self.market = market
        self.coin_base, self.coin_target = market.split('-')

        self.orderbook = _get_orderbook(market)
        self.wallet = Wallet()
        self.transaction_type = transaction_type
        # dictionary (hashset) 이용시 키 이름까지 byte() 배열이 되버린다.
        self.fee = _fee[self.coin_base]

        self.nexts = []
        if front is not None:
            self.front = front # connect linked list
            self.wallet = copy(front.wallet)

        self.logger = create_logger('transaction_%s' % market)

    # front 객체까지 반복하여 올라갑니다.
    def __str__(self):
        tree = []

        def recursive(current: Transaction):
            tree.append('%s(%s / %4s)' % (
                current.coin_current, current.market,
                'BUY' if current.transaction_type is TRX_BUY else 'SELL'
            ))
            return recursive(current.front) if current.front else None

        recursive(self)
        tree.reverse()
        return " -> ".join(tree)


    @classmethod
    def try_create(cls, market, transaction_type):
        # TODO : fix?
        if market not in _orderbooks.keys(): return None
        return cls(market, transaction_type)

    def calculate(self):
        # 유닛 데이터 불러오기
        # Orderbook에서 캐싱 최적화를 작성해 놓았으니 걱정 ㄴㄴ
        units = self.orderbook.units

        if self.transaction_type == TRX_BUY:
            balance, amount = vt_buy_all(
                balance=self.wallet.get(self.coin_base),
                fee=0,
                ask_prices=units[ASK_PRICES],
                ask_amounts=units[ASK_AMOUNTS]
            )
            self.wallet.set(self.coin_base, balance)
            self.wallet.set(self.coin_target, amount)
            self.logger.debug("calculated TRX_BUY balance=%.8f amount=%.8f" % (
                balance, amount
            ))

        if self.transaction_type == TRX_SELL:
            balance, amount = vt_sell_all(
                amount=self.wallet.get(self.coin_target),
                fee=0,
                bid_prices=units[BID_PRICES],
                bid_amounts=units[BID_AMOUNTS]
            )
            self.wallet.set(self.coin_base, balance)
            self.wallet.set(self.coin_target, amount)
            self.logger.debug("calculated TRX_SELL balance=%.8f amount=%.8f" % (
                balance, amount
            ))


    def attach(self, tr):
        ## TODO: detect duplicated mounting!
        assert isinstance(tr, Transaction)
        tr.front = self
        self.nexts.append(tr)

    # 업데이트하고, 호가 반영이 된 트랜젝션들을 반환합니다.
    def update_gen(self):
        if not self.is_start:
            self.wallet.update(self.front.wallet)

        self.calculate()
        if self.is_terminal: yield self
        else:
            for n in self.nexts:  # type: Transaction
                n.update()


    def update(self):
        ## TODO: update last nodes -> yielding?
        # update() -> 위 오브젝트부터 순서대로 진행하게 된다.
        if not self.is_start:
            self.wallet.update(self.front.wallet)

        self.calculate()
        if self.is_terminal: return
        for n in self.nexts: # type: Transaction
            n.update()