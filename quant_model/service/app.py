from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "It's up!"


@app.route('/generate_signal', methods=['PUT'])
def generate_signal():

    # Trigger data fetching
    # Generate signal
    # Send orders

    return jsonify({"response": "success"})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
