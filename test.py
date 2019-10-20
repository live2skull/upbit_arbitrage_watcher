from dotenv import load_dotenv
load_dotenv()

import os, sys
import redis


from json import loads

from dunamu import apis, misc, calculator, orderbook
from dunamu.orderbook import ASK_AMOUNTS, ASK_PRICES,\
    BID_AMOUNTS, BID_PRICES, LAST_REQUEST_TIME, LAST_UPDATE_TIME

from dunamu.topology import Topology
from dunamu.transaction import Wallet, Transaction, TRX_SELL, TRX_BUY
from dunamu.apis import UnsterblichContractClient

# https://datascienceschool.net/view-notebook/148fc57f684c4dc48eeb5048ab0d45f2/

def api():
    API = apis.UpbitAPIClient()
    print(API.get_market_status('ETH-GNT')['market']['state'])

def calc():
    order = orderbook.Orderbook('KRW-BTC')
    units = order.units

    # 잘 돌아가는것 같기도....
    balance, amount = calculator.vt_buy_all(13500000, 0.05, units[ASK_PRICES], units[ASK_AMOUNTS])
    print(balance, amount)


    balance, amount = calculator.vt_sell_all(0.23510001, 0.05, units[BID_PRICES], units[BID_AMOUNTS])
    print(balance, amount)


def verify_orderbook():
    pool = misc.create_redis_pool()
    r = redis.StrictRedis(connection_pool=pool)

    err = []

    keys = r.keys('*_last_*')
    for k in keys:
        k = k.decode()
        val = int(r.get(k).decode())
        if val is not 0:
            print('%s is %s : OK!' % (k, val))
        else:
            err.append(k)

    print(" ".join(err))


def generate_topology():
    wallet = Wallet()
    wallet.set('KRW', 200000)
    top = Topology.create_via_base('KRW', wallet=wallet, cycle=1)
    # print(top.print)
    # print(len(top))

    top.update_and_verify()

def wallet():
    # {"market":"KRW-WAXP","trx_type":"BUY"},
    # {"market":"ETH-WAXP","trx_type":"SELL"},
    # {"market":"KRW-ETH","trx_type":"SELL"}


    client = apis.UnsterblichContractClient()
    client.contract_chained_transactions([], 1000)

    return

    client = apis.UnsterblichAPIClient()
    print(client.get_available_topology(base_coin='KRW', balance=100000))


    return
    t = Transaction(market='KRW-WAXP', transaction_type=TRX_BUY)
    t.wallet.set('KRW', 200000)

    t.attach(
        Transaction(market='ETH-WAXP', transaction_type=TRX_SELL)
    )
    t.nexts[0].attach(
        Transaction(market='KRW-ETH', transaction_type=TRX_SELL)
    )


    target = t.nexts[0].nexts[0]

    t.update()
    print(target.wallet.account)


def wallet2():

    obj = loads('[[{"market":"KRW-WAXP","trx_type":"BUY"},{"market":"ETH-WAXP","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}]]')


    top = Topology.deserialize({
        'topology_top': 'KRW', 'objects': obj
    })
    top.wallet.set('KRW', 200000)
    top.update_and_verify()


def pika_send():
    connection = misc.create_pika_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange='orderbook', exchange_type='topic')

    message = ' '.join(sys.argv[1:]) or "info: Hello World!"
    channel.basic_publish(exchange='orderbook', routing_key='', body=message)
    print(" [x] Sent %r" % message)
    connection.close()


def test():
    print (apis.UpbitLocalClient().all_markets)

def deserialize_topology():
    s = '{"length":176,"topology_top":"KRW","cycle":1,"objects":[[{"market":"KRW-WAXP","trx_type":"BUY"},{"market":"ETH-WAXP","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-WAXP","trx_type":"BUY"},{"market":"BTC-WAXP","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-TSHP","trx_type":"BUY"},{"market":"BTC-TSHP","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-SOLVE","trx_type":"BUY"},{"market":"BTC-SOLVE","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ATOM","trx_type":"BUY"},{"market":"BTC-ATOM","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-AERGO","trx_type":"BUY"},{"market":"BTC-AERGO","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-TTC","trx_type":"BUY"},{"market":"BTC-TTC","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-MANA","trx_type":"BUY"},{"market":"ETH-MANA","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-MANA","trx_type":"BUY"},{"market":"BTC-MANA","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ENJ","trx_type":"BUY"},{"market":"BTC-ENJ","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-COSM","trx_type":"BUY"},{"market":"BTC-COSM","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-MOC","trx_type":"BUY"},{"market":"BTC-MOC","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-BTT","trx_type":"BUY"},{"market":"BTC-BTT","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-BSV","trx_type":"BUY"},{"market":"BTC-BSV","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ELF","trx_type":"BUY"},{"market":"BTC-ELF","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-UPP","trx_type":"BUY"},{"market":"BTC-UPP","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-MFT","trx_type":"BUY"},{"market":"BTC-MFT","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-OST","trx_type":"BUY"},{"market":"BTC-OST","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-CVC","trx_type":"BUY"},{"market":"ETH-CVC","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-CVC","trx_type":"BUY"},{"market":"BTC-CVC","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-RFR","trx_type":"BUY"},{"market":"BTC-RFR","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-DMT","trx_type":"BUY"},{"market":"ETH-DMT","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-DMT","trx_type":"BUY"},{"market":"BTC-DMT","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-BAT","trx_type":"BUY"},{"market":"ETH-BAT","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-BAT","trx_type":"BUY"},{"market":"BTC-BAT","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ADX","trx_type":"BUY"},{"market":"ETH-ADX","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-ADX","trx_type":"BUY"},{"market":"BTC-ADX","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-BCH","trx_type":"BUY"},{"market":"ETH-BCH","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-BCH","trx_type":"BUY"},{"market":"BTC-BCH","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-LOOM","trx_type":"BUY"},{"market":"BTC-LOOM","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-SRN","trx_type":"BUY"},{"market":"ETH-SRN","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-SRN","trx_type":"BUY"},{"market":"BTC-SRN","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ZRX","trx_type":"BUY"},{"market":"ETH-ZRX","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-ZRX","trx_type":"BUY"},{"market":"BTC-ZRX","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-POLY","trx_type":"BUY"},{"market":"BTC-POLY","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ZIL","trx_type":"BUY"},{"market":"BTC-ZIL","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-DCR","trx_type":"BUY"},{"market":"BTC-DCR","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-IGNIS","trx_type":"BUY"},{"market":"BTC-IGNIS","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-GTO","trx_type":"BUY"},{"market":"BTC-GTO","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-SC","trx_type":"BUY"},{"market":"ETH-SC","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-SC","trx_type":"BUY"},{"market":"BTC-SC","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-MCO","trx_type":"BUY"},{"market":"ETH-MCO","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-MCO","trx_type":"BUY"},{"market":"BTC-MCO","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-TRX","trx_type":"BUY"},{"market":"ETH-TRX","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-TRX","trx_type":"BUY"},{"market":"BTC-TRX","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-STORM","trx_type":"BUY"},{"market":"ETH-STORM","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-STORM","trx_type":"BUY"},{"market":"BTC-STORM","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-EOS","trx_type":"BUY"},{"market":"BTC-EOS","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-POWR","trx_type":"BUY"},{"market":"ETH-POWR","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-POWR","trx_type":"BUY"},{"market":"BTC-POWR","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-SBD","trx_type":"BUY"},{"market":"BTC-SBD","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ADA","trx_type":"BUY"},{"market":"ETH-ADA","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-ADA","trx_type":"BUY"},{"market":"BTC-ADA","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-EMC2","trx_type":"BUY"},{"market":"BTC-EMC2","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-REP","trx_type":"BUY"},{"market":"ETH-REP","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-REP","trx_type":"BUY"},{"market":"BTC-REP","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-VTC","trx_type":"BUY"},{"market":"BTC-VTC","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-GRS","trx_type":"BUY"},{"market":"BTC-GRS","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-STORJ","trx_type":"BUY"},{"market":"BTC-STORJ","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ARK","trx_type":"BUY"},{"market":"BTC-ARK","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-KMD","trx_type":"BUY"},{"market":"BTC-KMD","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ARDR","trx_type":"BUY"},{"market":"BTC-ARDR","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-XLM","trx_type":"BUY"},{"market":"ETH-XLM","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-XLM","trx_type":"BUY"},{"market":"BTC-XLM","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-STEEM","trx_type":"BUY"},{"market":"BTC-STEEM","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-LSK","trx_type":"BUY"},{"market":"BTC-LSK","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-GNT","trx_type":"BUY"},{"market":"ETH-GNT","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-GNT","trx_type":"BUY"},{"market":"BTC-GNT","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-QTUM","trx_type":"BUY"},{"market":"ETH-QTUM","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-QTUM","trx_type":"BUY"},{"market":"BTC-QTUM","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-XEM","trx_type":"BUY"},{"market":"ETH-XEM","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-XEM","trx_type":"BUY"},{"market":"BTC-XEM","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-WAVES","trx_type":"BUY"},{"market":"ETH-WAVES","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-WAVES","trx_type":"BUY"},{"market":"BTC-WAVES","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-SNT","trx_type":"BUY"},{"market":"ETH-SNT","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-SNT","trx_type":"BUY"},{"market":"BTC-SNT","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-OMG","trx_type":"BUY"},{"market":"ETH-OMG","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-OMG","trx_type":"BUY"},{"market":"BTC-OMG","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ETC","trx_type":"BUY"},{"market":"ETH-ETC","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-ETC","trx_type":"BUY"},{"market":"BTC-ETC","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-XRP","trx_type":"BUY"},{"market":"ETH-XRP","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-XRP","trx_type":"BUY"},{"market":"BTC-XRP","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-STRAT","trx_type":"BUY"},{"market":"ETH-STRAT","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-STRAT","trx_type":"BUY"},{"market":"BTC-STRAT","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-LTC","trx_type":"BUY"},{"market":"ETH-LTC","trx_type":"SELL"},{"market":"KRW-ETH","trx_type":"SELL"}],[{"market":"KRW-LTC","trx_type":"BUY"},{"market":"BTC-LTC","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-MTL","trx_type":"BUY"},{"market":"BTC-MTL","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-WAXP","trx_type":"BUY"},{"market":"KRW-WAXP","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-BCH","trx_type":"BUY"},{"market":"KRW-BCH","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-STORM","trx_type":"BUY"},{"market":"KRW-STORM","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-DMT","trx_type":"BUY"},{"market":"KRW-DMT","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-ADA","trx_type":"BUY"},{"market":"KRW-ADA","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-TRX","trx_type":"BUY"},{"market":"KRW-TRX","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-ZRX","trx_type":"BUY"},{"market":"KRW-ZRX","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-SRN","trx_type":"BUY"},{"market":"KRW-SRN","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-POWR","trx_type":"BUY"},{"market":"KRW-POWR","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-MANA","trx_type":"BUY"},{"market":"KRW-MANA","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-REP","trx_type":"BUY"},{"market":"KRW-REP","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-ADX","trx_type":"BUY"},{"market":"KRW-ADX","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-MCO","trx_type":"BUY"},{"market":"KRW-MCO","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-XLM","trx_type":"BUY"},{"market":"KRW-XLM","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-BAT","trx_type":"BUY"},{"market":"KRW-BAT","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-GNT","trx_type":"BUY"},{"market":"KRW-GNT","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-QTUM","trx_type":"BUY"},{"market":"KRW-QTUM","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-XEM","trx_type":"BUY"},{"market":"KRW-XEM","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-WAVES","trx_type":"BUY"},{"market":"KRW-WAVES","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-SNT","trx_type":"BUY"},{"market":"KRW-SNT","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-SC","trx_type":"BUY"},{"market":"KRW-SC","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-CVC","trx_type":"BUY"},{"market":"KRW-CVC","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-OMG","trx_type":"BUY"},{"market":"KRW-OMG","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-ETC","trx_type":"BUY"},{"market":"KRW-ETC","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-XRP","trx_type":"BUY"},{"market":"KRW-XRP","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-STRAT","trx_type":"BUY"},{"market":"KRW-STRAT","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"ETH-LTC","trx_type":"BUY"},{"market":"KRW-LTC","trx_type":"SELL"}],[{"market":"KRW-ETH","trx_type":"BUY"},{"market":"BTC-ETH","trx_type":"SELL"},{"market":"KRW-BTC","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-WAXP","trx_type":"BUY"},{"market":"KRW-WAXP","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-TSHP","trx_type":"BUY"},{"market":"KRW-TSHP","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-EOS","trx_type":"BUY"},{"market":"KRW-EOS","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ATOM","trx_type":"BUY"},{"market":"KRW-ATOM","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-COSM","trx_type":"BUY"},{"market":"KRW-COSM","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-AERGO","trx_type":"BUY"},{"market":"KRW-AERGO","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-TTC","trx_type":"BUY"},{"market":"KRW-TTC","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-SOLVE","trx_type":"BUY"},{"market":"KRW-SOLVE","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-BTT","trx_type":"BUY"},{"market":"KRW-BTT","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ELF","trx_type":"BUY"},{"market":"KRW-ELF","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-BSV","trx_type":"BUY"},{"market":"KRW-BSV","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-OST","trx_type":"BUY"},{"market":"KRW-OST","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ZIL","trx_type":"BUY"},{"market":"KRW-ZIL","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-MOC","trx_type":"BUY"},{"market":"KRW-MOC","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-MTL","trx_type":"BUY"},{"market":"KRW-MTL","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ENJ","trx_type":"BUY"},{"market":"KRW-ENJ","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-UPP","trx_type":"BUY"},{"market":"KRW-UPP","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-RFR","trx_type":"BUY"},{"market":"KRW-RFR","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-LOOM","trx_type":"BUY"},{"market":"KRW-LOOM","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-MFT","trx_type":"BUY"},{"market":"KRW-MFT","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-BCH","trx_type":"BUY"},{"market":"KRW-BCH","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-GTO","trx_type":"BUY"},{"market":"KRW-GTO","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-STORM","trx_type":"BUY"},{"market":"KRW-STORM","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-POLY","trx_type":"BUY"},{"market":"KRW-POLY","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-DMT","trx_type":"BUY"},{"market":"KRW-DMT","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-TRX","trx_type":"BUY"},{"market":"KRW-TRX","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ZRX","trx_type":"BUY"},{"market":"KRW-ZRX","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-SRN","trx_type":"BUY"},{"market":"KRW-SRN","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-IGNIS","trx_type":"BUY"},{"market":"KRW-IGNIS","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-POWR","trx_type":"BUY"},{"market":"KRW-POWR","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-SBD","trx_type":"BUY"},{"market":"KRW-SBD","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-MANA","trx_type":"BUY"},{"market":"KRW-MANA","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ADA","trx_type":"BUY"},{"market":"KRW-ADA","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-EMC2","trx_type":"BUY"},{"market":"KRW-EMC2","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-REP","trx_type":"BUY"},{"market":"KRW-REP","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-VTC","trx_type":"BUY"},{"market":"KRW-VTC","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-GRS","trx_type":"BUY"},{"market":"KRW-GRS","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-STORJ","trx_type":"BUY"},{"market":"KRW-STORJ","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ADX","trx_type":"BUY"},{"market":"KRW-ADX","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ARK","trx_type":"BUY"},{"market":"KRW-ARK","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-KMD","trx_type":"BUY"},{"market":"KRW-KMD","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ARDR","trx_type":"BUY"},{"market":"KRW-ARDR","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-MCO","trx_type":"BUY"},{"market":"KRW-MCO","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-XLM","trx_type":"BUY"},{"market":"KRW-XLM","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-DCR","trx_type":"BUY"},{"market":"KRW-DCR","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-STEEM","trx_type":"BUY"},{"market":"KRW-STEEM","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-LSK","trx_type":"BUY"},{"market":"KRW-LSK","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-BAT","trx_type":"BUY"},{"market":"KRW-BAT","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-GNT","trx_type":"BUY"},{"market":"KRW-GNT","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-QTUM","trx_type":"BUY"},{"market":"KRW-QTUM","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-XEM","trx_type":"BUY"},{"market":"KRW-XEM","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-WAVES","trx_type":"BUY"},{"market":"KRW-WAVES","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-SNT","trx_type":"BUY"},{"market":"KRW-SNT","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-SC","trx_type":"BUY"},{"market":"KRW-SC","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-CVC","trx_type":"BUY"},{"market":"KRW-CVC","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-OMG","trx_type":"BUY"},{"market":"KRW-OMG","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ETC","trx_type":"BUY"},{"market":"KRW-ETC","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-XRP","trx_type":"BUY"},{"market":"KRW-XRP","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-STRAT","trx_type":"BUY"},{"market":"KRW-STRAT","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-LTC","trx_type":"BUY"},{"market":"KRW-LTC","trx_type":"SELL"}],[{"market":"KRW-BTC","trx_type":"BUY"},{"market":"BTC-ETH","trx_type":"BUY"},{"market":"KRW-ETH","trx_type":"SELL"}]]}'
    obj = loads(s)

    top = Topology.deserialize(obj)
    print(top)


def main():
    func = sys.argv[1]

    if func == 'verify_orderbook':
        verify_orderbook()
    elif func == 'test':
        test()
    elif func == 'pika_send':
        pika_send()
    elif func == 'calc':
        calc()
    elif func == 'topology':
        generate_topology()
    elif func == 'api':
        api()
    elif func == 'wallet':
        wallet()
    elif func == 'wallet2':
        wallet2()
    elif func == 'dtop':
        deserialize_topology()

if __name__ == '__main__':
    main()