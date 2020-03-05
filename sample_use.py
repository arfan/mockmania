import logging
import os
import sys
import uuid
from pathlib import Path
from time import sleep

import requests
from main import get_mocks_folder

SERVICE_HOST = os.getenv('HOST')
SERVICE_PORT = os.getenv('PORT')

if not SERVICE_HOST:
    SERVICE_HOST = "localhost"
if not SERVICE_PORT:
    SERVICE_PORT = 7000

BASE_URL = "http://{}:{}".format(SERVICE_HOST, SERVICE_PORT)

print("SERVICE_HOST", SERVICE_HOST)
print("SERVICE_PORT", SERVICE_PORT)
print("BASE_URL", BASE_URL)

# create test mocks folder file name
test_mocks_folder = str(uuid.uuid1())

# set mocks folder to test_mock
result = requests.put('{}/mocks_folder'.format(BASE_URL), data=test_mocks_folder)
print(result.text)
sleep(1)
new_mock_folder = get_mocks_folder()
assert new_mock_folder == test_mocks_folder

# create test_mocks folder if not exist
Path(test_mocks_folder).mkdir(exist_ok=True)

# call mock api with some random string, this should create new file inside
# mocks folder and the result contains CHANGEME string
result = requests.get('{}/{}'.format(BASE_URL, str(uuid.uuid1())))
assert 'CHANGEME' in result.text

# write new mocks in folder
text_file = open(test_mocks_folder+'/hello.yaml', "w")
n = text_file.write("""method: GET
path: hello
response: 'Hello, World!'
""")
text_file.close()

# call mock hello api
result = requests.get('{}/hello'.format(BASE_URL))
assert result.text == 'Hello, World!'

# set mock output
requests.put('{}/mock_output'.format(BASE_URL), data="MOCK_OUTPUT")

# asssert mock_output file exist
assert os.path.exists('mock_output')

# call mock hello api
result = requests.get('{}/hello'.format(BASE_URL))
assert result.text == 'MOCK_OUTPUT'

# asssert mock_output file not exist
assert not os.path.exists('mock_output')

# call again mock hello api, should return previous result
result = requests.get('{}/hello'.format(BASE_URL))
assert result.text == 'Hello, World!'

# write new mocks in folder, hello with reference
text_file = open(test_mocks_folder+'/hello_reference.yaml', "w")
text_file.write("""method: GET
path: hello_reference
reference: {}/hello
""".format(BASE_URL))
text_file.close()

# call mock hello reference api, should return same result as hello
result = requests.get('{}/hello_reference'.format(BASE_URL))
assert result.text == 'Hello, World!'


# write new mocks in folder
text_file = open(test_mocks_folder+'/with_param.yaml', "w")
text_file.write("""method: GET
path: users/.*/details
response: |
  {
    "name": "user one",
    "address": "user address"
  }
""")
text_file.close()

# call user api with parameter
result = requests.get('{}/users/123413523/details'.format(BASE_URL))
result_json = result.json()

assert result_json.get('name') == 'user one'
assert result_json.get('address') == 'user address'


# write new mocks in folder
text_file = open(test_mocks_folder+'/with_param_body.yaml', "w")
text_file.write("""method: POST
path: users
body: '{"user": ".*"}'
response: |
  {
    "msg": "ok message"
  }
""")
text_file.close()

# call user api with parameter
result = requests.post('{}/users'.format(BASE_URL), json={"user": "1232132"})
result_json = result.json()

assert result_json.get('msg') == 'ok message'


# call user api without parameter
result = requests.post('{}/users'.format(BASE_URL))
assert 'CHANGEME' in result.text
