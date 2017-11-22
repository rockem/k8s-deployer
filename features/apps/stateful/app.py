import flask
from flask import Flask, Response

app = Flask(__name__)
_state = False


@app.route('/health')
def api_health():
    return flask.jsonify({'status': {'code': 'UP'}})


@app.route('/run')
def run():
    global _state
    _state = True
    return Response('State was changed to true.', status=200)


@app.route('/state')
def state():
    global _state
    return flask.jsonify({'state': _state})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
