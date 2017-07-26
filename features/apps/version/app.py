import os

import flask
from flask import Flask

app = Flask(__name__)


@app.route('/health')
def api_health():
    if os.getenv('APP_VERSION') == 'sick':
        raise RuntimeError()
    else:
        return flask.jsonify({'status': {'code': 'UP'}})


@app.route('/version')
def version():
    return flask.jsonify({'version': os.getenv('APP_VERSION')})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
