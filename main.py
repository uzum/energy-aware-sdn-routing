from flask import Flask, jsonify
from look_up_service import LookupService
app = Flask(__name__)
lookup = LookupService()

@app.route("/")
def hello():
    return jsonify(**lookup.onContentRequest('test'))

if __name__ == "__main__":
    app.run()
