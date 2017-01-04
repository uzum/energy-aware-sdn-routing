import sys
import httplib
import json
from config import *

class FloodlightAPI():
    def __init__(self, topology):
        self.server = CONTROLLER_IP
        self.request('POST', '/wm/statistics/config/enable/json', {})
        self.topology = topology

    def request(self, method, path, data):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        body = json.dumps(data)
        connection = httplib.HTTPConnection(self.server, CONTROLLER_API_PORT)
        connection.request(method, path, body, headers)
        response = connection.getresponse().read()
        connection.close()
        try:
            return json.loads(response)
        except ValueError:
            return { 'error': 'Cannot parse response' }

    def collectBandwidth(self):
        return self.request('GET', '/wm/statistics/bandwidth/all/all/json', {})

    def collectPorts(self):
        return self.request('GET', '/wm/core/switch/all/port/json', {})

    def summary(self):
        return self.request('GET', '/wm/core/controller/summary/json', {})

    def links(self):
        return self.request('GET', '/wm/topology/links/json', {})

    def device(self, ipv4):
        response = self.request('GET', '/wm/device/?ipv4=' + ipv4, {})
        if (response['devices']):
            return response['devices'][0]
        else:
            raise Exception('Cannot find a device with ip ' + ipv4)

    def setFlow(self, args):
        self.request('POST', '/wm/staticflowpusher/json', args)

    def flows(self, switch):
        response = self.request('GET', '/wm/staticflowpusher/list/' + switch + '/json', {})
        if (len(response[switch]) == 0):
            return []
        return [flow.keys()[0] for flow in response[switch]]

    def deleteFlow(self, args):
        self.request('DELETE', '/wm/staticflowpusher/json', args)
