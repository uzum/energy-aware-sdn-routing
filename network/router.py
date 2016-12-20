import sys
import random
from config import *

class Router():
    def __init__(self, topology, api):
        self.topology = topology
        self.api = api

    def calculate(self, host, locations):
        randomBaseLocation = locations['base'][random.randint(0, len(locations['base']) - 1)]
        randomEnhancementLocation = locations['enhancement'][random.randint(0, len(locations['enhancement']) - 1)]

        routes = {}
        # return a random route for the base layer for the random base location
        routes['base'] = [{
            'host': host,
            'destination': randomBaseLocation,
            # just randomly select some switches (it's not checked if they are connected or not)
            '_path': [switch.name for switch in self.topology.switches if random.random() < 0.3]
        }]
        # return 2 routes for the enhancement layer:
        #   first one is selected randomly for the random enhancement location
        #   second one is a fixed one to h7, passing through s1 and s2
        routes['enhancement'] = [{
            'host': host,
            'destination': randomEnhancementLocation,
            # just randomly select some switches (it's not checked if they are connected or not)
            '_path': [switch.name for switch in self.topology.switches if random.random() < 0.3]
        }, {
            'host': host,
            'destination': 'h7',
            '_path': ['s1', 's2']
        }]
        return routes
