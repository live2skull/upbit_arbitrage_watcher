import signal, os, sys

from dotenv import load_dotenv
load_dotenv()

from optparse import OptionParser
from json import loads
import math

from dunamu.topology import Topology, TopologyPredictionDaemon
from dunamu.apis import UnsterblichAPIClient

from os import getenv

parser = OptionParser()
parser.add_option("-c", "--cpu", dest="cpu",
                  help="cpu amount", metavar="CPU")
parser.add_option("-f", "--file", dest="file",
                  help="topology file", metavar="FILE")
parser.add_option('-b', '--basecoin', dest="basecoin",
                  help="base coin", metavar='DEST')
parser.add_option('-l', '--balance', dest="balance",
                  help="balance", metavar='balance')


## TODO: argument parser (optionparser를 통합으로 운용)
## TODO: python-pip / python3-pip 혼용 금지 및 requirements 패키지 관리하기
## TODO: venv 이용하기

MIN_ALLOW = float(getenv('TOPOLOGY_MAX_ALLOW', None))
MAX_ALLOW = float(getenv('TOPOLOGY_MIN_ALLOW', None))

# assert not MIN_ALLOW is None
# assert not MAX_ALLOW is None

class Bucket:
    data = None

# http://hleecaster.com/python-how-to-split-a-list-into-chunks/
def list_comprehension(my_list: list, n):
    return [my_list[i * n:(i + 1) * n] for i in range((len(my_list) + n - 1) // n )]

def main():

    daemons = []

    def signal_handler(sig, frame):
        print("!!! ** warm shutdown. please wait... ")
        for _daemon in daemons: # type: TopologyPredictionDaemon
            _daemon.shutdown()
        print("!!! now exit.")
        exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    (option, args) = parser.parse_args()

    base_coin = option.basecoin
    balance = float(option.balance)

    top_bucket = Bucket()

    if option.file:
        # read topology from file
        path = sys.path[0] + "\\" +  option.file if os.name == 'nt' else option.file
        top_bucket.data = loads(open(file=path).read())
    else:
        # read topology from server
        print("[!] load topology from server. please wait...")
        client = UnsterblichAPIClient()
        top_bucket.data = client.get_available_topology(base_coin=base_coin, balance=balance)

    topology_size = len(Topology.deserialize(top_bucket.data))
    topology_per_cpu = math.ceil(topology_size / int(option.cpu))

    print("topology_size: %s" % topology_size)
    print("topology_per_cpu: %s" % topology_per_cpu)

    market = top_bucket.data['topology_top']
    _topologies = list_comprehension(top_bucket.data['objects'], topology_per_cpu)

    for _top in _topologies:
        daemon = TopologyPredictionDaemon(topology=Topology.deserialize({
            'topology_top' : market, 'objects' : _top
        }), base=option.basecoin, balance=float(option.balance),
            max_allow=MAX_ALLOW, min_allow=MIN_ALLOW
        )
        daemons.append(daemon)

    for daemon in daemons:
        daemon.start()

    while True:
        input()


if __name__ == '__main__':
    main()