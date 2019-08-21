from .transaction import Transaction
from .misc import create_logger, create_redis_pool, keys2floats

from .apis import UpbitLocalClient


TERMS = {
    1 : 3, 2 : 4
}

_upbitLocalClient = UpbitLocalClient()


def get_buyable_list(base_coin):
    markets = _upbitLocalClient.all_markets

    results = list(filter(lambda x: x.split(',')[0] == base_coin, markets))
    return results


def get_sellable_list(target_coin):
    markets = _upbitLocalClient.all_markets

    results = list(filter(lambda x: x.split(',')[0] == target_coin, markets))
    return results


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

    def __init__(self, source_coin):
        self.source_coin = source_coin

    def explore_transactions_bfs_gen(self):
        pass

    # 업데이트가 필요한 트랜젝션만 찾아서 재계산(update) 수행 후 검증하면 됩니다.
    def update_and_verify(self, market):
        pass

    # 전체 트랜젝션을 순서대로 재계산 후 검증하면 됩니다.
    def refresh_and_verify(self):
        pass

    # save / load - 실행하면 자기 자신에서 그리게 됩니다.
    def save(self):
        pass

    def load(self):
        pass

    @classmethod
    def create_via_base(cls, base_coin: str, cycle=1, cached=True, save=False):
        if cycle not in TERMS.keys(): raise ValueError("Invalid cycle!")

        new_topology = cls(base_coin)
        new_topology.endpoint_type = ENDPOINT_BASE
        new_topology.transaction_entries = get_buyable_list(new_topology.source_coin)

        max_term = TERMS[cycle]
        term = 1

        def build(tr: Transaction, term: int):
            term += 1

            if term == max_term:
                pass
                # Transaction.try_create
                # ...
            else:
                # non - default process


        for __tr in new_topology.transaction_entries:
            # 여기서 빌드가 실패하는 경우는 없으니 그대로 전체를 실행하면 됩니다.
            build(__tr, term)



    @classmethod
    def create_via_target(cls, target_coin, cycle=1, cached=True, save=False):
        if cycle not in TERMS.keys(): raise ValueError("Invalid cycle!")

        new_topology = cls(target_coin)
        new_topology.endpoint_type = ENDPOINT_TARGET
        new_topology.transaction_entries = get_buyable_list(new_topology.source_coin)