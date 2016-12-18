import sys

class Switch():
    def __init__(self, name):
        self.name = name
        self.switches = []
        self.hosts = []
class Host():
    def __init__(self, name):
        self.name = name
class Topology():
    def __init__(self):
        topology = [{'hosts': [1, 2, 3], 'switches': [2, 4, 5, 6]},
            {'hosts': [], 'switches': [1, 3, 4]},
            {'hosts': [4, 5, 6], 'switches': [2, 4, 7, 8]},
            {'hosts': [], 'switches': [1, 2, 3, 6, 7]},
            {'hosts': [7, 8, 9], 'switches': [1, 6]},
            {'hosts': [], 'switches': [1, 4, 5]},
            {'hosts': [], 'switches': [3, 4, 8]},
            {'hosts': [10, 11, 12], 'switches': [3, 7]}]
        self.switches = []
        self.hosts = []

        for idx, switch in enumerate(topology):
            switchObject = Switch( 's' + str(idx + 1) )
            switch['switchObject'] = switchObject
            self.switches.append(switchObject)
            for host in switch['hosts']:
                hostObject = Host( 'h' + str(host))
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
        sys.stderr.write('\n')
