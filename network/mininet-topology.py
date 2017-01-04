"""Custom topology for the project
8 switches connected with a mesh-like topology. 4 of the switches have 3 different hosts.
"""

from mininet.topo import Topo

class CustomTopology(Topo):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )
        topology = [{'hosts': [1, 2, 3], 'switches': [2, 4, 5, 6]},
         {'hosts': [4], 'switches': [3, 4]},
         {'hosts': [5, 6, 7], 'switches': [4, 7, 8]},
         {'hosts': [8], 'switches': [6, 7]},
         {'hosts': [9, 10, 11], 'switches': [6]},
         {'hosts': [12], 'switches': [7]},
         {'hosts': [13], 'switches': [8]},
         {'hosts': [14, 15, 16], 'switches': []}]

        for idx, switch in enumerate(topology):
            switch['selfObject'] = self.addSwitch( 's' + str(idx + 1) )
            for host in switch['hosts']:
                host = self.addHost('h' + str(host))
                self.addLink(switch['selfObject'], host);

        for switch in topology:
            for neighbor in switch['switches']:
                self.addLink(switch['selfObject'], topology[neighbor - 1]['selfObject'])

topos = { 'custom': ( lambda: CustomTopology() ) }
