from flask import Flask, jsonify, request

# from data.extrac
from werkzeug.exceptions import BadRequest

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/start_bot', methods=['PUT'])
def start_bot():

    try:
        data = request.get_json(force=True)
    except BadRequest:
        pass

    return jsonify({"response": "success"})


@app.route('/stop_bot')
def stop_bot():

    # Stops the data collection stream
    # closes any open positions

    pass


if __name__ == "__main__":
    app.run(host='0.0.0.0')
