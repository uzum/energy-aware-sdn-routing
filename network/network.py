import json
import sys

from router import Router
from content_store import ContentStore
from flow_pusher import FlowPusher
from topology import Topology

class Network():
    def __init__(self, APIConstructor):
        self.topology = Topology()
        self.api = APIConstructor(self.topology)
        self.router = Router(self.topology, self.api)
        self.contentStore = ContentStore(self.topology)
        self.flowPusher = FlowPusher(self.topology, self.api)
        self.latestStats = None

        # fill out port maps for switches
        self.topology.fillPortMaps(self.api.links())
        # fill out attachment ports for each host
        for host in self.topology.hosts:
            host.attachmentPort = self.api.device(host.ipv4)['attachmentPoint'][0]['port']

        #debug
        self.contentStore.printLocations()
        self.topology.printTopology()

    def request(self, host, strategy, content):
        locations = self.contentStore.find(content)
        routes = self.router.calculate(strategy, host, locations)
        for route in routes['base']:
            self.flowPusher.push(route)
            self.contentStore.updateCachesAlongPath(content, 'base', route['_path'])
        for route in routes['enhancement']:
            self.flowPusher.push(route)
            self.contentStore.updateCachesAlongPath(content, 'enhancement', route['_path'])
        self.contentStore.printLocations()
        return routes

    def incrementalStats(self):
        response = {}
        currentStats = self.api.collectPorts()
        if (self.latestStats == None):
            self.latestStats = currentStats

        for switch, stats in currentStats.iteritems():
            switchObject = self.topology.get('s' + switch[len(switch) - 1])
            portStats = stats['port_reply'][0]['port']
            response[switchObject.name] = {}
            for index, port in enumerate(portStats):
                if (port['port_number'] != 'local'):
                    if (int(port['port_number']) in switchObject.portMap):
                        neighbor = switchObject.portMap[int(port['port_number'])]
                        currentrx = port['receive_packets']
                        currenttx = port['transmit_packets']
                        lastrx = self.latestStats[switch]['port_reply'][0]['port'][index]['receive_packets']
                        lasttx = self.latestStats[switch]['port_reply'][0]['port'][index]['transmit_packets']
                        response[switchObject.name][neighbor.name] = int(currentrx) + int(currenttx) - int(lastrx) - int(lasttx)
        self.latestStats = currentStats
        return response
