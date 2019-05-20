import flask
from flask import Flask

app = Flask(__name__)


@app.route('/health')
def api_health():
        return flask.jsonify({'status': {'code': 'UP'}})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
