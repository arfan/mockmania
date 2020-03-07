import json
import os
import sys
import time
from http import HTTPStatus
from os import path

import requests
import yaml
from flask import Flask, Response, abort
from flask import request

import re

app = Flask(__name__)
HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

endpoint_set_mocks_folder = 'mocks_folder'
endpoint_set_mock_output = 'mock_output'
endpoint_write_mock_file = 'mock_write'

mock_output_file_name = 'mock_output'
mocks_folder_file_name = 'mocks_folder'


def set_mocks_folder(mock_list_folder):
    with open(mocks_folder_file_name, "w") as text_file:
        text_file.write(mock_list_folder)


def set_mock_output(mock_output):
    with open(mock_output_file_name, "w") as text_file:
        text_file.write(mock_output)


def get_response(filepath, current_request, origin_request):
    with open(filepath) as file:
        m = yaml.load(file, Loader=yaml.FullLoader)

        if m.get('method'):
            if not m.get('method') == current_request.get('method'):
                return None

        if m.get('path') is not None:
            if current_request.get('path') is None:
                return None
            if re.fullmatch(m.get('path'), current_request.get('path')) is None:
                return None

        if m.get('body'):
            if current_request.get('body') is None:
                return None
            if re.fullmatch(m.get('body'), current_request.get('body')) is None:
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

            # excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            # headers = [(name, value) for (name, value) in resp.raw.headers.items()
            #            if name.lower() not in excluded_headers]

            current_request['reference'] = reference
            write_mock_yaml_file(filepath, current_request, resp.content.decode())

            return resp.content

        return response


def get_mocks_folder():
    if path.exists(mocks_folder_file_name):
        with open(mocks_folder_file_name, 'r') as file:
            mock_list_folder = file.read().replace('\n', '')
            return mock_list_folder
    else:
        return "mocks"


def read_mock_list(mock_list_folder):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(mock_list_folder):
        for file in f:
            files.append(os.path.join(r, file))

    return files


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def handler(path):
    # check default output
    if os.path.isfile(mock_output_file_name):
        content = open(mock_output_file_name, 'r').read()
        os.remove(mock_output_file_name)
        return content

    req = {
        'method': request.method,
    }

    qs = request.query_string.decode()
    if qs:
        req['path'] = "{}?{}".format(path, request.query_string.decode())
    else:
        req['path'] = path

    # special command/request
    if request.method != 'GET':
        body_content = json.dumps(request.json)

        if body_content != 'null':
            req['body'] = body_content

        if req['method'] == 'PUT' and req['path'] == endpoint_set_mocks_folder:
            set_mocks_folder(request.data.decode())
            return Response(response='{"msg":"ok"}',
                            status=200,
                            mimetype="application/json")

        if req['method'] == 'PUT' and req['path'] == endpoint_set_mock_output:
            set_mock_output(request.data.decode())

            return Response(response='{"msg":"ok"}',
                            status=200,
                            mimetype="application/json")

        if req['method'] == 'PUT' and req['path'] == endpoint_write_mock_file:
            file_content = request.data.decode()
            yaml_parse = yaml.safe_load(file_content)
            location = yaml_parse.get('location')

            if not location or not location.endswith('.yaml') or location.startswith("/"):
                return Response(response='{"msg":"location not valid"}',
                                status=HTTPStatus.BAD_REQUEST,
                                mimetype="application/json")
            write_raw_mock_yaml_file(location, file_content)
            return Response(response='{"msg":"ok"}',
                            status=200,
                            mimetype="application/json")

    mock_list_folder = get_mocks_folder()
    mock_list = read_mock_list(mock_list_folder)

    for ml in mock_list:
        resp = get_response(ml, req, request)
        if resp:
            if resp == 'abort(504)':
                abort(504)
            return Response(response=resp,
                            status=200,
                            mimetype="application/json")

    filename = get_mock_filename(path, mock_list_folder)
    response_text = "CHANGEME in file {}".format(filename)

    # create new mock list
    try:
        write_mock_yaml_file(filename, req, response_text)
    except Exception as e:
        return Response(response='{"msg":"fail to write file, please check mocks folder"}',
                            status=HTTPStatus.INTERNAL_SERVER_ERROR,
                            mimetype="application/json")
    return response_text


def get_mock_filename(path, mock_list_folder):
    milliseconds = int(round(time.time() * 1000))
    filename = "{}/{}_{}_{}.yaml".format(mock_list_folder, request.method, path.replace('/', '_'),
                                         str(milliseconds))
    return filename


def represent_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def write_mock_yaml_file(filename, req, response_text):
    try:
        text_file = open(filename, "w")
        req['response'] = response_text
        text_file.write(yaml.dump(req))
        text_file.close()
    except Exception as e:
        raise e


def write_raw_mock_yaml_file(filename, file_content):
    try:
        text_file = open(filename, "w")
        text_file.write(file_content)
        text_file.close()
    except Exception as e:
        raise e

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if represent_int(sys.argv[1]):
            app.run(host='0.0.0.0', port=int(sys.argv[1]))
        else:
            print("Usage python main.py [port]")
    else:
        app.run(host='0.0.0.0', port=7000)