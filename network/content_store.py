import sys
import random
from collections import deque
from config import *

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
        self.caches = [switch for switch in self.topology.switches if random.random() < CACHE_PROBABILITY]
        # randomly allocate base and enhancement layers to the hosts initially
        for item, locations in self.library.iteritems():
            hostCount = random.randint(2, len(self.topology.hosts) * HOST_WITH_CONTENT_PROBABILITY)
            for index in range(0, hostCount):
                randomHost = self.topology.hosts[random.randint(0, len(self.topology.hosts) - 1)]
                if (randomHost.isCache): continue
                if (index % 2 == 0):
                    if (randomHost not in locations['base']):
                        locations['base'].append(randomHost)
                else:
                    if (randomHost not in locations['enhancement']):
                        locations['enhancement'].append(randomHost)

    def find(self, content):
        if (content not in self.library):
            raise Exception(content + ' not found in the content store')
        cachedBaseLayers = [switch.cacheHost.name for switch in self.caches if (content in switch.cache['base'])]
        cachedEnhancementLayer = [switch.cacheHost.name for switch in self.caches if (content in switch.cache['enhancement'])]
        return {
            'content': content,
            'base': cachedBaseLayers + [host.name for host in self.library[content]['base']],
            'enhancement': cachedEnhancementLayer + [host.name for host in self.library[content]['enhancement']]
        }

    def updateCachesAlongPath(self, content, layer, path):
        for node in path:
            switchObject = self.topology.get(node)
            if (switchObject in self.caches and content not in switchObject.cache[layer]):
                # it's a LRU cache, so remove the first item if it's full
                if (len(switchObject.cache[layer]) == CACHE_SIZE):
                    switchObject.cache[layer].popleft()
                switchObject.cache[layer].append(content)

    def printLocations(self):
        sys.stderr.write('Current Cache Map:\n')
        for switch in self.caches:
            sys.stderr.write('  Switch ' + switch.name + ' (cache host: ' + switch.cacheHost.name + ')\n')
            sys.stderr.write('    Cached base layers: ' + ', '.join([str(item) for item in switch.cache['base']]) + '\n')
            sys.stderr.write('    Cached enhancement layers: ' + ', '.join([str(item) for item in switch.cache['enhancement']]) + '\n')
        sys.stderr.write('Content Locations:\n')
        for item, locations in self.library.iteritems():
            sys.stderr.write('  Content ' + item + ':\n')
            sys.stderr.write('    Base: ' + ', '.join(
                [l.name for l in locations['base']] +
                [switch.cacheHost.name for switch in self.caches if (item in switch.cache['base'])]
            ) + '\n')
            sys.stderr.write('    Enhancement: ' + ', '.join(
                [l.name for l in locations['enhancement']] +
                [switch.cacheHost.name for switch in self.caches if (item in switch.cache['enhancement'])]
            ) + '\n')
        sys.stderr.write('\n')
