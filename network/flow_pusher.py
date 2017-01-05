import sys

class FlowPusher():
    def __init__(self, topology, api):
        self.topology = topology
        self.api = api

    def clearOldFlows(self, host, destination):
        for switch in self.topology.switches:
            dpid = '00:00:00:00:00:00:00:0' + switch.name[1]
            flows = self.api.flows(dpid)
            for flow in flows:
                if (flow.startswith(host + ':' + destination)):
                    sys.stderr.write('deleting a flow in ' + switch.name + ', ' + host + ' > ' + destination + '\n')
                    self.api.deleteFlow({
                        'name': flow,
                        'switch': dpid
                    })

    def push(self, route):
        # self.api.clearAllFlows()
        self.clearOldFlows(route['host'], route['destination'])
        sys.stderr.write('creating a path from ' + route['host'] + ' to ' + route['destination'] + ':\n')

        src = self.topology.getHost(route['host'])
        dst = self.topology.getHost(route['destination'])

        for index, switch in enumerate(route['_path']):
            currentSwitch = self.topology.get(switch)

            # if it's the first switch in the path, in_port connects to the source host
            if (index == 0):
                in_port = src.attachmentPort
            else:
                in_port = currentSwitch.getAttachmentPort(route['_path'][index - 1])

            # if it's the last switch in the path, out_port connects to the destination host
            if (index == len(route['_path']) - 1):
                out_port = dst.attachmentPort
            else:
                out_port = currentSwitch.getAttachmentPort(route['_path'][index + 1])

            if (in_port == -1 or out_port == -1):
                raise Exception('Cannot find the correct attachment ports for switch ' + currentSwitch.name)

            sys.stderr.write('  creating flow#' + str(index)+ ' in ' + currentSwitch.name + '\n')
            sys.stderr.write('    in_port: ' + str(in_port) + ' out_port: ' + str(out_port) + '\n')
            sys.stderr.write('    src_ipv4: ' + src.ipv4 + ' dst_ipv4: ' + dst.ipv4 + '\n')

            self.api.setFlow({
                'switch': '00:00:00:00:00:00:00:0' + currentSwitch.name[1],
                'name': route['host'] + ':' + route['destination'] + '|' + currentSwitch.name + '.f',
                'ipv4_src': src.ipv4,
                'ipv4_dst': dst.ipv4,
                'eth_type': '0x800',
                'cookie': '0',
                'priority': '32768',
                'in_port': str(in_port),
                'active': 'true',
                'actions': 'output=' + str(out_port),
            })

            self.api.setFlow({
                'switch': '00:00:00:00:00:00:00:0' + currentSwitch.name[1],
                'name': route['host'] + ':' + route['destination'] + '|' + currentSwitch.name + '.farp',
                'arp_spa': src.ipv4,
                'arp_tpa': dst.ipv4,
                'eth_type': '0x806',
                'cookie': '0',
                'priority': '32768',
                'in_port': str(in_port),
                'active': 'true',
                'actions': 'output=' + str(out_port),
            })

            self.api.setFlow({
                'switch': '00:00:00:00:00:00:00:0' + currentSwitch.name[1],
                'name': route['host'] + ':' + route['destination'] + '|' + currentSwitch.name + '.r',
                'ipv4_src': dst.ipv4,
                'ipv4_dst': src.ipv4,
                'eth_type': '0x800',
                'cookie': '0',
                'priority': '32768',
                'in_port': str(out_port),
                'active': 'true',
                'actions': 'output=' + str(in_port),
            })

            self.api.setFlow({
                'switch': '00:00:00:00:00:00:00:0' + currentSwitch.name[1],
                'name': route['host'] + ':' + route['destination'] + '|' + currentSwitch.name + '.rarp',
                'arp_spa': dst.ipv4,
                'arp_tpa': src.ipv4,
                'eth_type': '0x806',
                'cookie': '0',
                'priority': '32768',
                'in_port': str(out_port),
                'active': 'true',
                'actions': 'output=' + str(in_port),
            })
