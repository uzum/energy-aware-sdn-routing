import sys

from router import Router
from content_store import ContentStore
from flow_pusher import FlowPusher
from topology import Topology

class Network():
    def __init__(self):
        self.topology = Topology()
        self.topology.printTopology()
        self.router = Router(self.topology)
        self.contentStore = ContentStore(self.topology)
        self.contentStore.printLocations()
        self.flowPusher = FlowPusher(self.topology)

    def request(self, host, content):
        locations = self.contentStore.find(content)
        routes = self.router.calculate(host, locations)
        for route in routes['base']:
            self.flowPusher.push(route)
            self.contentStore.updateCachesAlongPath(content, 'base', route['_path'])
        for route in routes['enhancement']:
            self.flowPusher.push(route)
            self.contentStore.updateCachesAlongPath(content, 'enhancement', route['_path'])
        self.contentStore.printLocations()
        return routes
