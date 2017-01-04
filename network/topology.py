import sys
import json
import random
from collections import deque
from config import *

class Switch():
    def __init__(self, name):
        self.name = name
        self.switches = []
        self.hosts = []
        self.cache = {
            'base': deque([]),
            'enhancement': deque([])
        }
        self.cacheHost = None
        self.portMap = {}
        energyRandom = random.random()
        if (energyRandom < LOW_ENERGY_SWITCH_PROB):
            self.energyClass = 'low'
        elif (energyRandom < LOW_ENERGY_SWITCH_PROB + MEDIUM_ENERGY_SWITCH_PROB):
            self.energyClass = 'medium'
        else:
            self.energyClass = 'high'

    def getAttachmentPort(self, switchName):
        for port in self.portMap:
            if (self.portMap[port].name == switchName):
                return port
        raise Exception(switchName + ' is not connected to ' + self.name)

class Host():
    def __init__(self, name, switch):
        self.name = name
        self.switch = switch
        self.ipv4 = '10.0.0.' + name[1:]
        self.isCache = False
        # describes the port of the SWITCH this host is connected to
        self.attachmentPort = None

class Topology():
    def __init__(self):
        topology = [{'hosts': [1, 2, 3], 'switches': [2, 4, 5, 6]},
            {'hosts': [4], 'switches': [1, 3, 4]},
            {'hosts': [5, 6, 7], 'switches': [2, 4, 7, 8]},
            {'hosts': [8], 'switches': [1, 2, 3, 6, 7]},
            {'hosts': [9, 10, 11], 'switches': [1, 6]},
            {'hosts': [12], 'switches': [1, 4, 5, 7]},
            {'hosts': [13], 'switches': [3, 4, 6, 8]},
            {'hosts': [14, 15, 16], 'switches': [3, 7]}]
        self.switches = []
        self.hosts = []

        for idx, switch in enumerate(topology):
            switchObject = Switch( 's' + str(idx + 1) )
            switch['switchObject'] = switchObject
            self.switches.append(switchObject)
            for hostIdx, host in enumerate(switch['hosts']):
                hostObject = Host('h' + str(host), switchObject)
                self.hosts.append(hostObject)
                switchObject.hosts.append(hostObject)
                if (hostIdx == 0):
                    hostObject.isCache = True
                    switchObject.cacheHost = hostObject

        for switch in topology:
            for neighbor in switch['switches']:
                switch['switchObject'].switches.append(topology[neighbor - 1]['switchObject'])

    def printTopology(self):
        sys.stderr.write('Current Topology:\n')
        for switch in self.switches:
            sys.stderr.write('  Switch ' + switch.name + ' (' + switch.energyClass + '):\n')
            sys.stderr.write('    neighbor switches: [' + ', '.join([s.name for s in switch.switches]) + ']\n')
            sys.stderr.write('    neighbor hosts: [' + ', '.join([h.name for h in switch.hosts]) + ']\n')
            sys.stderr.write('    ports:\n')
            for port in switch.portMap:
                sys.stderr.write('      port#' + str(port) + ': ' + switch.portMap[port].name + '\n')
            sys.stderr.write('  Cache host: ' + switch.cacheHost.name + '\n')
        for host in self.hosts:
            sys.stderr.write('  Host ' + host.name + ' -> ipv4: ' + host.ipv4 + ', attachment port: ' + host.attachmentPort + '\n')
        sys.stderr.write('\n')

    def get(self, name):
        if (name[0] == 'h'):
            return self.getHost(name)
        return self.getSwitch(name)

    def getSwitch(self, name):
        return next(switch for switch in self.switches if switch.name == name)

    def getHost(self, name):
        return next(host for host in self.hosts if host.name == name)

    def fillPortMaps(self, links):
        for link in links:
            source = self.get('s' + link['src-switch'][len(link['src-switch']) - 1])
            destination = self.get('s' + link['dst-switch'][len(link['dst-switch']) - 1])
            source.portMap[link['src-port']] = destination
            destination.portMap[link['dst-port']] = source
