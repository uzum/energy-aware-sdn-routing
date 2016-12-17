from flask import Flask, jsonify, request
from network import Network
app = Flask(__name__)
network = Network()

@app.route("/path/<string:content_name>")
def content_request(content_name):
    return jsonify(**network.request(request.args.get('host', ''), content_name))

if __name__ == "__main__":
    app.run()
