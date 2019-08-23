from .transaction import Transaction, TRX_BUY, TRX_SELL
from .misc import create_logger, create_redis_pool, keys2floats

from .apis import UpbitLocalClient


TERMS = {
    1 : 3, 2 : 4
}
SPECIAL_BASES = ['BTC', 'ETH']

_upbitLocalClient = UpbitLocalClient()


def get_buyable_list(base_coin):
    markets = _upbitLocalClient.all_markets

    results = list(filter(lambda x: x.split(',')[0] == base_coin, markets))
    return results


def get_sellable_list(target_coin):
    markets = _upbitLocalClient.all_markets

    results = list(filter(lambda x: x.split(',')[0] == target_coin, markets))
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
                ## TODO: 만약 기저통화가 KRW가 아닌 BTC, ETH인 경우
                ## XRP => BTC 형태로의 판매도 가능하다.
                ## 구매인 경우: BTC -> ETH (기저통화가 ETH)

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
                # 자기 자신이 기저 화폐인 경우 2가지 경우가 가능!
                if tr.coin_is_base:
                    for l in get_buyable_list(tr.coin_current):
                        _tr = Transaction.try_create(
                            market="%s-%s" % (tr.coin_base, l),
                            transaction_type=TRX_BUY
                        )
                        if _tr is None: continue
                        result = build(_tr, term) # 해당 object에 대해 recursive하게 노드 작성
                        if result:
                            tr.attach(_tr) # 해당 노드에 대한 작업 완료
                        else: # -> false!
                            # 삭제하고, 자기 자신까지만 삭제하면 된다. (at cycle=1)
                            # TODO: 또는 현재까지 depth를 확인해서 삭제할 것 정하기
                            # 이게 제일 중요할듯
                            pass

                    # ex) KRW-BTC 같은 형태
                    for _tr in create_transactions(
                            get_sellable_list(tr.coin_current), TRX_SELL):
                        if _tr is None: continue


                # 그렇지 않은 경우 한개의 경우만 가능.
                else:
                    # get_sellable_list => CNAME 이므로
                    #

                    pass


        for __tr in new_topology.transaction_entries:
            # 여기서 빌드가 실패하는 경우는 없으니 그대로 전체를 실행하면 됩니다.
            build(__tr, term)



    @classmethod
    def create_via_target(cls, target_coin, cycle=1, cached=True, save=False):
        if cycle not in TERMS.keys(): raise ValueError("Invalid cycle!")

        new_topology = cls(target_coin)
        new_topology.endpoint_type = ENDPOINT_TARGET
        new_topology.transaction_entries = get_buyable_list(new_topology.source_coin)