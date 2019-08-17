import sys, os


from dunamu import apis

def get_market_list(market_base: str):

    res = []
    markets = apis.get_all_market()
    for market in markets:
        m = market['market']
        if m.split('-')[0] == market_base:
            res.append(m)

    print(','.join(res))




def main():
    func = sys.argv[1]

    if func == 'market_list':
        get_market_list(sys.argv[2])


if __name__ == '__main__':
    main()