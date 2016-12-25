import sys
import random
import json
from config import *

class Router():
    def __init__(self, topology, api):
        self.topology = topology
        self.api = api

    def collectStatistics(self):
        cumulativeStats = {}
        for switch, stats in self.api.collectPorts().iteritems():
            switchObject = self.topology.get('s' + switch[len(switch) - 1])
            portStats = stats['port_reply'][0]['port']
            cumulativeStats[switchObject.name] = {}
            for port in portStats:
                if (port['port_number'] != 'local'):
                    if (int(port['port_number']) in switchObject.portMap):
                        neighbor = switchObject.portMap[int(port['port_number'])]
                        cumulativeStats[switchObject.name][neighbor.name] = port;

        for portStats in self.api.collectBandwidth():
            switchId = portStats['dpid']
            if (portStats['port'] != 'local'):
                switchObject = self.topology.get('s' + switchId[len(switchId) - 1])
                if (int(portStats['port']) in switchObject.portMap):
                    neighbor = switchObject.portMap[int(portStats['port'])]
                    cumulativeStats[switchObject.name][neighbor.name]['link-speed-bits-per-second'] = portStats['link-speed-bits-per-second']
                    cumulativeStats[switchObject.name][neighbor.name]['bits-per-second-rx'] = portStats['bits-per-second-rx']
                    cumulativeStats[switchObject.name][neighbor.name]['bits-per-second-tx'] = portStats['bits-per-second-tx']

        return cumulativeStats

    def calculateRandomRoute(self, host, locations):
        randomBaseLocation = locations['base'][random.randint(0, len(locations['base']) - 1)]
        randomEnhancementLocation = locations['enhancement'][random.randint(0, len(locations['enhancement']) - 1)]

        routes = {}
        # return a random route for the base layer for the random base location
        routes['base'] = [{
            'host': host,
            'destination': randomBaseLocation,
            # just randomly select some switches (it's not checked if they are connected or not)
            '_path': [switch.name for switch in self.topology.switches if random.random() < RAND_SWITCH_DENSITY]
        }]
        # return 2 routes for the enhancement layer:
        #   first one is selected randomly for the random enhancement location
        #   second one is a fixed one to h7, passing through s1 and s2
        routes['enhancement'] = [{
            'host': host,
            'destination': randomEnhancementLocation,
            # just randomly select some switches (it's not checked if they are connected or not)
            '_path': [switch.name for switch in self.topology.switches if random.random() < RAND_SWITCH_DENSITY]
        }, {
            'host': host,
            'destination': 'h7',
            '_path': ['s1', 's2']
        }]
        return routes

    def calculateLatencyOptimalRoute(self, host, locations):
        return self.calculateRandomRoute(host, locations)

    def calculateEnergyOptimalRoute(self, host, locations):
        sys.stderr.write(json.dumps(self.collectStatistics()) + '\n')
        return self.calculateRandomRoute(host, locations)

    def calculate(self, strategy, host, locations):
        if (strategy == 'random'):
            return self.calculateRandomRoute(host, locations)
        elif (strategy == 'energy'):
            return self.calculateEnergyOptimalRoute(host, locations)
        else:
            return self.calculateLatencyOptimalRoute(host, locations)
