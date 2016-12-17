from router import Router
from content_store import ContentStore
from flow_pusher import FlowPusher

class Network():
    def __init__(self):
        self.topology = {}
        self.router = Router(self.topology)
        self.contentStore = ContentStore(self.topology)
        self.flowPusher = FlowPusher(self.topology)

    def request(self, host, content):
        locations = self.contentStore.find(content)
        routes = self.router.calculate(host, locations)
        for route in routes['base']:
            self.flowPusher.push(route)
        for route in routes['enhancement']:
            self.flowPusher.push(route)
        return routes
