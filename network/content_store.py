import sys
import random

class ContentStore():
    def __init__(self, topology):
        self.topology = topology
        self.library = {
            'a': {'base':[], 'enhancement':[] },
            'b': {'base':[], 'enhancement':[] },
            'c': {'base':[], 'enhancement':[] },
            'd': {'base':[], 'enhancement':[] },
            'e': {'base':[], 'enhancement':[] },
            'f': {'base':[], 'enhancement':[] }
        }
        # randomly allocate base and enhancement layers to the hosts initially
        for item, locations in self.library.iteritems():
            hostCount = random.randint(2, len(self.topology.hosts) / 2)
            for index in range(0, hostCount):
                randomHost = self.topology.hosts[random.randint(0, len(self.topology.hosts) - 1)]
                if (index % 2 == 0):
                    if (randomHost not in locations['base']):
                        locations['base'].append(randomHost)
                else:
                    if (randomHost not in locations['enhancement']):
                        locations['enhancement'].append(randomHost)

    def find(self, content):
        if (content not in self.library):
            raise Exception(content + ' not found in the content store')
        return {
            'content': content,
            'base': self.library[content]['base'],
            'enhancement': self.library[content]['enhancement']
        }

    def printLocations(self):
        sys.stderr.write('Content Locations:\n')
        for item, locations in self.library.iteritems():
            sys.stderr.write('  Content ' + item + ':\n')
            sys.stderr.write('    Base: ' + ', '.join([l.name for l in locations['base']]) + '\n')
            sys.stderr.write('    Enhancement: ' + ', '.join([l.name for l in locations['enhancement']]) + '\n')
        sys.stderr.write('\n')
