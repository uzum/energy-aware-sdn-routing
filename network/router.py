class Router():
    def __init__(self, topology):
        self.topology = topology;

    def calculate(self, host, locations):
        routes = {};
        routes['base'] = [{
            'host': host,
            'destination': 'h2',
            '_path': ['s1', 's2', 's8']
        }]
        routes['enhancement'] = [{
            'host': host,
            'destination': 'h10',
            '_path': ['s1', 's4', 's6']
        }, {
            'host': host,
            'destination': 'h5',
            '_path': ['s7', 's8']
        }]
        return routes
