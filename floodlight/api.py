import sys
import httplib
import json
from config import *

class FloodlightAPI():
    def __init__(self, topology):
        self.server = 'http://' + CONTROLLER_IP
        #self.request('POST', '/wm/statistics/config/enable/json', {})
        self.topology = topology

    def request(self, method, path, data):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        body = json.dumps(data)
        connection = httplib.HTTPConnection(self.server, CONTROLLER_API_PORT)
        connection.request(method, path, body, headers)
        response = connection.getresponse()
        connection.close()
        return json.loads(response.read())

    def collectStatistics(self):
        return self.request('GET', '/wm/statistics/bandwidth/all/all/json')
