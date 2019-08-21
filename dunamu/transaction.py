
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
        for k,v in wallet.account:
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
        return self.coin_base if self.transaction_type is TRX_BUY else self.coin_target

    @property
    def coin_is_base(self):
        return self.coin_current in _coin_bases

    def __int__(self, market, transaction_type, front=None):
        self.market = market
        self.coin_base, self.coin_target = market.split('-')

        self.orderbook = _get_orderbook(market)
        self.wallet = Wallet()
        self.transaction_type = transaction_type
        self.fee = _fee[self.coin_base]

        self.nexts = []
        if front is not None:
            self.front = front # connect linked list
            self.wallet = copy(front.wallet)

        self.logger = create_logger('transaction_%s' % market)


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


    def update(self):
        # update() -> 위 오브젝트부터 순서대로 진행하게 된다.
        if not self.is_start:
            self.wallet.update(self.front.wallet)

        self.calculate()
        if self.is_terminal: return
        for next in self.nexts: # type: Transaction
            next.update()