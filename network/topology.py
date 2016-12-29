import sys
import json
from collections import deque

class Switch():
    def __init__(self, name):
        self.name = name
        self.switches = []
        self.hosts = []
        self.cache = {
            'base': deque([]),
            'enhancement': deque([])
        }
        self.portMap = {}

    def getAttachmentPort(self, switchName):
        for port in self.portMap:
            if (self.portMap[port].name == switchName):
                return port
        return -1

class Host():
    def __init__(self, name, switch):
        self.name = name
        self.switch = switch
        self.ipv4 = '10.0.0.' + name[1:]
        self.attachmentPort = None

class Topology():
    def __init__(self):
        topology = [{'hosts': [1, 2, 3], 'switches': [2, 4, 5, 6]},
            {'hosts': [], 'switches': [1, 3, 4]},
            {'hosts': [4, 5, 6], 'switches': [2, 4, 7, 8]},
            {'hosts': [], 'switches': [1, 2, 3, 6, 7]},
            {'hosts': [7, 8, 9], 'switches': [1, 6]},
            {'hosts': [], 'switches': [1, 4, 5, 7]},
            {'hosts': [], 'switches': [3, 4, 6, 8]},
            {'hosts': [10, 11, 12], 'switches': [3, 7]}]
        self.switches = []
        self.hosts = []

        for idx, switch in enumerate(topology):
            switchObject = Switch( 's' + str(idx + 1) )
            switch['switchObject'] = switchObject
            self.switches.append(switchObject)
            for host in switch['hosts']:
                hostObject = Host('h' + str(host), switchObject)
                self.hosts.append(hostObject)
                switchObject.hosts.append(hostObject)

        for switch in topology:
            for neighbor in switch['switches']:
                switch['switchObject'].switches.append(topology[neighbor - 1]['switchObject'])

    def printTopology(self):
        sys.stderr.write('Current Topology:\n')
        for switch in self.switches:
            sys.stderr.write('  Switch ' + switch.name + ':\n')
            sys.stderr.write('    neighbor switches: [' + ', '.join([s.name for s in switch.switches]) + ']\n')
            sys.stderr.write('    neighbor hosts: [' + ', '.join([h.name for h in switch.hosts]) + ']\n')
            sys.stderr.write('    ports:\n')
            for port in switch.portMap:
                sys.stderr.write('      port#' + str(port) + ': ' + switch.portMap[port].name + '\n')
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
