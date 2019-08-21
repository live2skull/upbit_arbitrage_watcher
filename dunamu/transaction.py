from .orderbook import Orderbook
from .calculator import vt_buy_all, vt_sell_all
from copy import copy

class Market:
    pass


'''
Orderbook 오브젝트 생성 시 마다 내부적으로 redis 커넥션을 다시 만들게 되므로,
프로그램 실행시 필요한 오브젝트를 사전에 생성 완료한 후 유지하여야 한다.

'''

## 전체 마켓 코인리스트를 가져와서 ["":""] 쌍으로 설정

class Wallet:

    wallet = None # type: dict

    def insert(self, coin, amount):
        self.wallet.setdefault(coin, float(amount))
        self.wallet[coin] = float(amount)

    def __init__(self):
        self.wallet = dict()


TRX_BUY = 0
TRX_SELL = 1

# virtual transaction implementation!
class Transaction:

    market = None # type: str

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

    def __int__(self, market, transaction_type, front=None):
        self.market = market
        self.wallet = Wallet()

        self.transaction_type = transaction_type

        self.nexts = []
        if front is not None:
            self.front = front # connect linked list
            self.wallet = copy(front.wallet)

    def calculate(self):
        pass

    def update(self):
        self.calculate()
        for next in self.nexts: # type: Transaction
            next.update()