import os
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
    SERVICE_PORT = 30000

BASE_URL = "http://{}:{}".format(SERVICE_HOST, SERVICE_PORT)

print("SERVICE_HOST", SERVICE_HOST)
print("SERVICE_PORT", SERVICE_PORT)
print("BASE_URL", BASE_URL)

# create test mocks folder file name
print("----")
print("create test mocks folder file name")
test_mocks_folder = "SAMPLE_USE_"+str(uuid.uuid1())
print("test mock folder filename", test_mocks_folder)

print("----")
print("set mocks folder to test_mock")
result = requests.put('{}/mocks_folder'.format(BASE_URL), data=test_mocks_folder)
print("result", result.text)
print("sleep 1 second to make sure api called properly")
sleep(1)

new_mocks_folder = get_mocks_folder()
print("new mock folder", new_mocks_folder)
print("test mock folder", test_mocks_folder)
assert new_mocks_folder == test_mocks_folder

# create test_mocks folder if not exist
print("----")
print("create test mocks folder if not exist")
Path(test_mocks_folder).mkdir(exist_ok=True)

# call mock api with some random string, this should create new file inside
# mocks folder and the result contains CHANGEME string
print("----")
print("call mock api with some random string, this should create new file inside mock folder")
print("and the result contains CHANGEME string")
result = requests.get('{}/{}'.format(BASE_URL, str(uuid.uuid1())))
print("result", result.text)
assert 'CHANGEME' in result.text

print("----")
print("write new mocks in folder")
text_file = open(test_mocks_folder+'/hello.yaml', "w")
n = text_file.write("""method: GET
path: hello
response: 'Hello, World!'
""")
text_file.close()

# call mock hello api
print("----")
print("call mock hello api")
result = requests.get('{}/hello'.format(BASE_URL))
print("result", result.text)
assert result.text == 'Hello, World!'

# set mock output
print("----")
print("set mock output")
requests.put('{}/mock_output'.format(BASE_URL), data="MOCK_OUTPUT")

# asssert mock_output file exist
assert os.path.exists('mock_output')

# call mock hello api
print("----")
print("call mock hello api")
result = requests.get('{}/hello'.format(BASE_URL))
print("result", result.text)
assert result.text == 'MOCK_OUTPUT'

# asssert mock_output file not exist
assert not os.path.exists('mock_output')

# call again mock hello api, should return previous result
print("----")
print("call again mock hello api, should return previous result")
result = requests.get('{}/hello'.format(BASE_URL))
print("result", result.text)
assert result.text == 'Hello, World!'

# write new mocks in folder, hello with reference
print("----")
print("write new mocks in folder, hello with reference")
text_file = open(test_mocks_folder+'/hello_reference.yaml', "w")
text_file.write("""method: GET
path: hello_reference
reference: {}/hello
""".format(BASE_URL))
text_file.close()

# call mock hello reference api, should return same result as hello
print("----")
print("call mock hello reference api, should return same result as hello")
result = requests.get('{}/hello_reference'.format(BASE_URL))
print("result", result.text)
assert result.text == 'Hello, World!'


# write new mocks in folder
print("----")
print("write new mocks in folder")
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
print("----")
print("call user api with parameter")
result = requests.get('{}/users/123413523/details'.format(BASE_URL))
print("result", result.text)
result_json = result.json()

assert result_json.get('name') == 'user one'
assert result_json.get('address') == 'user address'


# write new mocks in folder
print("----")
print("write new mocks in folder")
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
print("----")
print("call user api with parameter")
result = requests.post('{}/users'.format(BASE_URL), json={"user": "1232132"})
print("result", result.text)
result_json = result.json()

assert result_json.get('msg') == 'ok message'

# call user api without parameter
print("----")
print("call user api without parameter, should create new mock file and result in CHANGEME...")
result = requests.post('{}/users'.format(BASE_URL))
print("result", result.text)
assert 'CHANGEME' in result.text


# write mock file via api
print("----")
print("write mock file via api")
location = test_mocks_folder+'/hello_from_write.yaml'
result = requests.put('{}/mock_write'.format(BASE_URL), data="""location: """+location+"""
method: GET
path: hello_from_write
response: '{"message":"hello from write"}'
delete: true
""")
result_json = result.json()
print("result", result.text)
assert result_json.get('msg') == 'ok'


print("----")
print("call new written mock api")
result = requests.get('{}/hello_from_write'.format(BASE_URL))
assert result.json().get('message')=='hello from write'


print("call new written mock api")
result = requests.get('{}/hello_from_write'.format(BASE_URL))
assert result.text.startswith("CHANGEME")
