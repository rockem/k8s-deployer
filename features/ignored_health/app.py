import flask
from flask import Flask

app = Flask(__name__)

@app.route('/ignore')
def ignore():
    return flask.jsonify(dict(status=dict(code='UP')))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8080)