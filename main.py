import json
import os
import time

import requests
import yaml
from flask import Flask, Response, abort
from flask import request
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

mockmania_endpoint = 'mockmania'
mockmania_output = 'mockmania_output'
mock_list_folder_file = 'mock_list_folder'


def set_mock_list_folder(mock_list_folder):
    text_file = open(mock_list_folder_file, "w")
    n = text_file.write(mock_list_folder)
    text_file.close()


def set_mock_mania_output(mock_output):
    text_file = open(mockmania_output, "w")
    n = text_file.write(mock_output)
    text_file.close()


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

        # check default output
        if os.path.isfile(mockmania_output):
            content = open(mockmania_output, 'r').read()
            os.remove(mockmania_output)
            return content

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
            # headers = [(name, value) for (name, value) in resp.raw.headers.items()
            #            if name.lower() not in excluded_headers]

            current_request['reference'] = reference
            write_yaml_file(filepath, current_request, resp.content.decode())

            return resp.content

        return response


def get_mock_list_folder():
    with open(mock_list_folder_file, 'r') as file:
        mock_list_folder = file.read().replace('\n', '')
        return mock_list_folder


def read_mock_list(mock_list_folder):
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
    }

    qs = request.query_string.decode()
    if qs:
        req['path'] = "{}?{}".format(path, request.query_string.decode())
    else:
        req['path'] = path

    if request.method != 'GET':
        body_content = json.dumps(request.json)

        if body_content != 'null':
            req['body'] = body_content

        if req['method'] == 'PUT' and req['path'] == mockmania_endpoint:
            set_mock_list_folder(request.data.decode())
            return Response(response={"msg":"ok"},
                            status=200,
                            mimetype="application/json")

        if req['method'] == 'PUT' and req['path'] == mockmania_output:
            set_mock_mania_output(request.data.decode())

            return Response(response={"msg":"ok"},
                            status=200,
                            mimetype="application/json")

    mock_list_folder = get_mock_list_folder()
    mock_list = read_mock_list(mock_list_folder)

    for ml in mock_list:
        resp = get_response(ml, req, request)
        if resp:
            if resp == 'abort(504)':
                abort(504)
            return Response(response=resp,
                            status=200,
                            mimetype="application/json")

    filename = get_filename(path, mock_list_folder)
    response_text = "CHANGEME in file {}".format(filename)

    # create new mock list
    write_yaml_file(filename, req, response_text)

    return response_text


def get_filename(path, mock_list_folder):
    milliseconds = int(round(time.time() * 1000))
    filename = "{}/{}_{}_{}.yaml".format(mock_list_folder, request.method, path.replace('/', '_'),
                                         str(milliseconds))
    return filename


def write_yaml_file(filename, req, response_text):
    text_file = open(filename, "w")
    req['response'] = response_text
    text_file.write(yaml.dump(req))
    text_file.close()


if __name__ == '__main__':
    print("Server start")
    http_server = WSGIServer(('', 7000), app)
    http_server.serve_forever()
