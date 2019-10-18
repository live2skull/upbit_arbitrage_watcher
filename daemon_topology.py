import signal, os

from dotenv import load_dotenv
load_dotenv()

from optparse import OptionParser
from json import loads
import math

from dunamu.topology import Topology, TopologyPredictionDaemon

parser = OptionParser()
parser.add_option("-c", "--cpu", dest="cpu",
                  help="cpu amount", metavar="CPU")
parser.add_option("-f", "--file", dest="file",
                  help="topology file", metavar="FILE")

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
            _daemon.join(timeout=5)
        print("!!! now exit.")
        exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    (option, args) = parser.parse_args()

    top_bucket = Bucket()

    if option.file:
        top_bucket.data = loads(open(file=option.file).read())
    else:
        raise ValueError()

    topology_size = len(top_bucket.data)
    topology_per_cpu = math.ceil(topology_size / int(option.cpu))

    market = top_bucket.data['topology_top']

    for _top in list_comprehension(top_bucket.data, topology_per_cpu):
        daemon = TopologyPredictionDaemon(topology=Topology.deserialize({
            'topology_top' : market, 'objects' : _top
        }))
        daemons.append(daemon)

    for daemon in daemons:
        daemon.start()

    while True:
        input()


if __name__ == '__main__':
    main()