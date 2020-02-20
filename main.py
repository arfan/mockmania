import json
import time

from flask import Flask, Response
from flask import request
import yaml
import os

import settings

app = Flask(__name__)
HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


def get_response(filepath, current_request):
    with open(filepath) as file:
        m = yaml.load(file, Loader=yaml.FullLoader)

        if m.get('method'):
            if not m.get('method') == current_request.get('method'):
                return None

        if m.get('path'):
            if not m.get('path') == current_request.get('path'):
                return None

        if m.get('body'):
            if not m.get('body') == current_request.get('body'):
                return None

        return m.get('response')


def read_mock_list():
    path = settings.mock_list_folder

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))

    return files


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def main_handler(path):
    req = {
        'method': request.method,
        'path': path,
        'body': json.dumps(request.json),
    }

    mock_list = read_mock_list()

    for ml in mock_list:
        resp = get_response(ml, req)
        if resp:
            return Response(response=resp,
                    status=200,
                    mimetype="application/json")

    # non supported requests, need to create new mock list
    milliseconds = int(round(time.time() * 1000))
    filename = "{}/{}_{}_{}.yaml".format(settings.mock_list_folder, request.method, path.replace('/', '_'), str(milliseconds))
    text_file = open(filename, "w")
    req['response'] = "CHANGEME in file {}".format(filename)
    n = text_file.write(yaml.dump(req))
    text_file.close()

    return "CHANGEME in file {}".format(filename)


if __name__ == '__main__':
    app.run(port=7000)