import json
import time

from flask import Flask, Response
from flask import request
import yaml
import os

import requests

app = Flask(__name__)
HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
mock_list_folder = 'mock_list'


def get_response(filepath, current_request, origin_request):
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

        response = m.get('response')

        if response is None:
            reference = m.get('reference')

            resp = requests.request(
                method=origin_request.method,
                url=reference,
                headers={key: value for (key, value) in origin_request.headers if key != 'Host'},
                data=origin_request.get_data(),
                cookies=origin_request.cookies,
                allow_redirects=False)

            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [(name, value) for (name, value) in resp.raw.headers.items()
                       if name.lower() not in excluded_headers]

            current_request['reference'] = reference
            write_yaml_file(filepath, current_request, resp.content.decode())

            return resp.content

        return response

def read_mock_list():
    path = mock_list_folder

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))

    return files


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def handler(path):
    req = {
        'method': request.method,
        'path': path,
    }

    body_content = json.dumps(request.json)

    if body_content != 'null':
        req['body'] = body_content

    mock_list = read_mock_list()

    for ml in mock_list:
        resp = get_response(ml, req, request)
        if resp:
            return Response(response=resp,
                            status=200,
                            mimetype="application/json")

    # non supported requests, need to create new mock list
    milliseconds = int(round(time.time() * 1000))
    filename = "{}/{}_{}_{}.yaml".format(mock_list_folder, request.method, path.replace('/', '_'),
                                         str(milliseconds))

    response_text = "CHANGEME in file {}".format(filename)

    write_yaml_file(filename, req, response_text)

    return response_text


def write_yaml_file(filename, req, response_text):
    text_file = open(filename, "w")
    req['response'] = response_text
    text_file.write(yaml.dump(req))
    text_file.close()


if __name__ == '__main__':
    app.run(port=7000)
