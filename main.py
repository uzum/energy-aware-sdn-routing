from flask import Flask, jsonify, request
from network import Network
from floodlight import FloodlightAPI

app = Flask(__name__)
network = Network(FloodlightAPI)

@app.route("/path/<string:route_strategy>/<string:content_name>")
def content_request(route_strategy, content_name):
    return jsonify(**network.request(request.args.get('host', ''), route_strategy, content_name))

if __name__ == "__main__":
    app.run()
