from .transaction import Transaction
from .misc import create_logger, create_redis_pool

from .apis import UpbitLocalClient


TERMS = {
    1 : 3, 2 : 4
}


upbitLocalClient = UpbitLocalClient()




#TODO: applying coroutine / lambda fast filtering
def get_buyable_list(base_coin):
    markets = upbitLocalClient.all_markets

    results = list(filter(lambda x: x.split(',')[0] == base_coin, markets))
    return results


def get_sellable_list(target_coin):
    markets = upbitLocalClient.all_markets

    results = list(filter(lambda x: x.split(',')[0] == target_coin, markets))
    return results


class Counter:
    term = None # type: int
    def __init__(self): self.term = 0
    def count(self): self.term += 1



class Topology:

    transaction_entries = None # type: list
    source_coin = None # type: str

    def __init__(self, source_coin):
        self.source_coin = source_coin

    def save(self):
        pass

    @classmethod
    def create_via_base(cls, base_coin: str, cycle=1, cached=True, save=False):
        if cycle not in TERMS.keys(): raise ValueError("Invalid cycle!")

        new_topology = cls(base_coin)
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
                pass


        for __tr in new_topology.transaction_entries:
            # 여기서 빌드가 실패하는 경우는 없으니 그대로 전체를 실행하면 됩니다.
            build(__tr, term)


    @classmethod
    def create_via_target(cls, target_coin, cycle=1, cached=True, save=False):
        pass