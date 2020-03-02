import os
import uuid
from pathlib import Path
from time import sleep

import requests
from main import get_mocks_folder

# create test mocks folder file name
test_mocks_folder = str(uuid.uuid1())

# set mocks folder to test_mock
requests.put('http://localhost:7000/mocks_folder', data=test_mocks_folder)
new_mock_folder = get_mocks_folder()
sleep(1)
assert new_mock_folder == test_mocks_folder

# create test_mocks folder if not exist
Path(test_mocks_folder).mkdir(exist_ok=True)

# call mock api with some random string, this should create new file inside
# mocks folder and the result contains CHANGEME string
result = requests.get('http://localhost:7000/{}'.format(str(uuid.uuid1())))
assert 'CHANGEME' in result.text

# write new mocks in folder
text_file = open(test_mocks_folder+'/hello.yaml', "w")
n = text_file.write("""method: GET
path: hello
response: 'Hello, World!'
""")
text_file.close()

# call mock hello api
result = requests.get('http://localhost:7000/hello')
assert result.text == 'Hello, World!'

# set mock output
requests.put('http://localhost:7000/mock_output', data="MOCK_OUTPUT")

# asssert mock_output file exist
assert os.path.exists('mock_output')

# call mock hello api
result = requests.get('http://localhost:7000/hello')
assert result.text == 'MOCK_OUTPUT'

# asssert mock_output file not exist
assert not os.path.exists('mock_output')

# call again mock hello api, should return previous result
result = requests.get('http://localhost:7000/hello')
assert result.text == 'Hello, World!'

# write new mocks in folder, hello with reference
text_file = open(test_mocks_folder+'/hello_reference.yaml', "w")
n = text_file.write("""method: GET
path: hello_reference
reference: http://localhost:7000/hello
""")
text_file.close()

# call mock hello reference api, should return same result as hello
result = requests.get('http://localhost:7000/hello_reference')
assert result.text == 'Hello, World!'
