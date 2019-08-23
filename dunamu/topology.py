import queue

from .transaction import Transaction, Wallet, TRX_BUY, TRX_SELL
from .misc import create_logger, create_redis_pool, keys2floats

from .apis import UpbitLocalClient


TERMS = {
    1 : 3, 2 : 4
}
SPECIAL_BASES = ['BTC', 'ETH']

_upbitLocalClient = UpbitLocalClient()
_markets = _upbitLocalClient.all_markets

## get_..._transactions
## -> 토폴로지로 사용될 데이터들이므로 트랜젝션을 만들어서 내보냅니다.
## ** 여기서 마켓 orderbook 정보가 가능한지 한번 더 판단함
## ** 마켓이 사용 가능한지도 반단.

def get_buyable_transactions(base_coin):
    results = []
    for market in _markets:
        base, target = market.split('-')

        if base == base_coin:
            tr = Transaction.try_create(
                market=market,
                transaction_type=TRX_BUY
            )
            if tr is not None: results.append(tr)

    return results


def get_sellable_transaction(target_coin):
    results = []
    for market in _markets:
        base, target = market.split('-')

        if target == target_coin:
            tr = Transaction.try_create(
                market=market,
                transaction_type=TRX_SELL
            )
            if tr is not None: results.append(tr)
    return results



def create_transactions(lists: list, transaction_type):
    for l in lists:
        yield Transaction.try_create(market=l, transaction_type=transaction_type)


class Counter:
    term = None # type: int
    def __init__(self): self.term = 0
    def count(self): self.term += 1



ENDPOINT_BASE = 0
ENDPOINT_TARGET = 1


class Topology:

    transaction_entries = None # type: list

    source_coin = None # type: str
    endpoint_type = None

    wallet = None # type: Wallet


    def __init__(self, source_coin):
        self.source_coin = source_coin
        self.transaction_entries = []
        self.wallet = Wallet()

    def __len__(self):
        i = 0
        for obj in self.endpoint_transactions_bfs_gen():
            i += 1
        return i


    @property
    def print(self):
        # __str__ 로 구현하지 않은 이유는 디버깅시 evaluation이 일어나므로 매우 느려질 수 있음!
        out = []
        for tr in self.endpoint_transactions_bfs_gen():
            out.append(str(tr))
        return "\n".join(out)


    def attach(self, transaction: Transaction):
        self.transaction_entries.append(transaction)


    def check_profit(self, transaction: Transaction):
        start_balance = self.wallet.get(self.source_coin)
        end_balance = transaction.wallet.get(self.source_coin)

        return end_balance > start_balance, end_balance - start_balance


    def explore_transactions_bfs_gen(self, market: str):
        q = queue.Queue()
        for tr in self.transaction_entries: q.put(tr)

        while not q.empty():
            tr = q.get() # type: Transaction
            if tr.market == market:
                yield tr
            else:
                for _tr in tr.nexts: q.put(_tr)


    def endpoint_transactions_bfs_gen(self):
        q = queue.Queue()
        for tr in self.transaction_entries: q.put(tr)

        while not q.empty():
            tr = q.get() # type: Transaction
            if tr.is_terminal:
                yield tr
            else:
                for _tr in tr.nexts: q.put(_tr)

    # 트랜젝션 재계산 요청
    # TODO: set initial wallet statement
    def update_and_verify(self, market=None):
        # market=None -> 전체 업데이트 요청이므로 바로 상위 트랜젝션에서 업데이트
        # market="" -> 매칭되는 오브젝트만 찾아서 해당 하위 오브젝트까지 업데이트 진행

        _engine = self.explore_transactions_bfs_gen(market) if market\
            else self.transaction_entries

        for tr in _engine: # type: Transaction
            for _tr in tr.update_gen(): # type: Transaction
                avail, profit = self.check_profit(_tr)
                if avail:
                    print("%s = %s" % (_tr, profit))

    # save / load - 실행하면 자기 자신에서 그리게 됩니다.
    def save(self):
        pass

    def load(self):
        pass

    # used for evaluate testing
    @classmethod
    def create_via_base_str(cls, base_str: str, tree_str: str, wallet:Wallet):
        transactions = tree_str.split(' -> ')

        term = 1
        max_term = len(transactions) - 1

        def build(term: int, tr: Transaction):
            pass

        build(term, transactions[0])

    @classmethod
    def create_via_base(cls, base_coin: str, wallet:Wallet, cycle=1, cached=True, save=False):
        if cycle not in TERMS.keys(): raise ValueError("Invalid cycle!")
        if wallet is None: raise ValueError("Invalid wallet!")

        new_topology = cls(base_coin)
        new_topology.wallet = wallet
        new_topology.endpoint_type = ENDPOINT_BASE

        max_term = TERMS[cycle]
        term = 1

        def build(tr: Transaction, term: int):
            term += 1

            # This process is last process
            if term == max_term:
                ## TODO: 만약 기저통화가 KRW가 아닌 BTC, ETH인 경우
                ## XRP => BTC 형태로의 판매도 가능하다.
                ## 구매인 경우: BTC -> ETH (기저통화가 ETH)

                # 여기에서는 이 하나만 사용하면 되므로 get_... method 사용 필요 없음.ㅋ
                if base_coin in SPECIAL_BASES and tr.coin_current in SPECIAL_BASES:
                    _tr = Transaction.try_create(
                        market="%s-%s" % (tr.coin_current, base_coin),
                        transaction_type=TRX_BUY
                    )

                else:
                    _tr = Transaction.try_create(
                        market="%s-%s" % (base_coin, tr.coin_current),
                        transaction_type=TRX_SELL
                    )

                if _tr is None:
                    return False

                tr.attach(_tr)
                return True

            else:

            # This process is initialization process
            ##########################

                # 기저화폐인 경우 get_buyable_transaction도 다시 사용할 수 있다.
                if tr.coin_is_base:
                    for _tr in get_buyable_transactions(tr.coin_current):
                        if build(_tr, term):
                            tr.attach(_tr)

                for _tr in get_sellable_transaction(tr.coin_current):
                    if build(_tr, term):
                        tr.attach(_tr)

                ## 마지막 프로세스가 아닌데 자식 노드가 없다면 빌드에 실패.
                ## 자신 노드가 필요없음.
                return not tr.is_terminal


        for __tr in get_buyable_transactions(base_coin):
            # 여기서 빌드가 실패하는 경우...? 가 발생한다면 attach 하지 않으면 됩니다.
            if build(__tr, term):
                __tr.wallet.update(new_topology.wallet) # 해당 값을 업로드합니다.
                new_topology.attach(__tr)

        return new_topology


    @classmethod
    def create_via_target(cls, target_coin, cycle=1, cached=True, save=False):
        if cycle not in TERMS.keys(): raise ValueError("Invalid cycle!")

        raise NotImplementedError("아직 구현되지 않았습니다.")

        # new_topology = cls(target_coin)
        # new_topology.endpoint_type = ENDPOINT_TARGET
        # new_topology.transaction_entries = get_buyable_list(new_topology.source_coin)