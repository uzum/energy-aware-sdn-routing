import sys

class FlowPusher():
    def __init__(self, topology, api):
        self.topology = topology
        self.api = api

    def push(self, route):
        sys.stderr.write('creating a path from ' + route['host'] + ' to ' + route['destination'] + ':\n')
        node = route['host']
        for switch in route['_path']:
            sys.stderr.write('  creating a flow from ' + node + ' to ' + switch + '\n')
            node = switch
        sys.stderr.write('  creating a flow from ' + node + ' to ' + route['destination'] + '\n\n')
        return
