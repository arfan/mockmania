import json

from flask import Flask
from flask import request
import yaml

app = Flask(__name__)

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def catch_all(path):
    # print(path)
    # print(request.method)
    # print(request.headers)
    print(request.json)

    req = {
        'body': json.dumps(request.json),
        'body2': "test \n test test\n   kuda",
        'method': request.method,
        'path': path,
    }

    return yaml.dump(req)

if __name__ == '__main__':
    app.run()