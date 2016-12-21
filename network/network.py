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
        self.topology.printTopology()
        self.router = Router(self.topology, self.api)
        self.contentStore = ContentStore(self.topology)
        self.contentStore.printLocations()
        self.flowPusher = FlowPusher(self.topology, self.api)
        sys.stderr.write(json.dumps(self.api.summary()))

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
