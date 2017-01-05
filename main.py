from flask import Flask, Markup, jsonify, request
from network import Network
from floodlight import FloodlightAPI

app = Flask(__name__)
network = Network(FloodlightAPI)

@app.route("/path/<string:route_strategy>/<string:content_name>")
def content_request(route_strategy, content_name):
    return jsonify(**network.request(request.args.get('host', ''), route_strategy, content_name))

@app.route("/stats")
def traffic_stats():
    stats = network.incrementalStats()
    response = '-\t' + '\t'.join(['<strong>s' + str(i) + '</strong>' for i in range(1, 9)]) + '\n'
    for srcIndex in range(1, 9):
        response = response + '<strong>s' + str(srcIndex) + '</strong>\t'
        for dstIndex in range(1, 9):
            if ('s' + str(dstIndex) in stats['s' + str(srcIndex)]):
                response = response + str(stats['s' + str(srcIndex)]['s' + str(dstIndex)]) + '\t'
            else:
                response = response + '-\t'
        response = response + '\n'
    return Markup('<img src="/static/topology.png" width="500" height="300"/><pre>' + response + '</pre>')

if __name__ == "__main__":
    app.run()
