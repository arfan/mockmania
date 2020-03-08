![Python application](https://github.com/arfan/mockmania/workflows/Python%20application/badge.svg)
<img src="https://img.shields.io/codecov/c/github/arfan/mockmania">

# Mockmania

Simple python mocking of http api, able to catch http request and 
directly modify the output. 
Any http request using any method, url path, and body payload directed to Mockmania
will create a yaml file inside a mock folder, in that file we can then change the 
desired response output.

Sample mock yaml file
```yaml
method: GET
path: hello
response: '{"message":"hello"}'
```

For example we run mockmania server in localhost and port 7000. If we hit the
api with:
```bash
curl http://localhost:7000/hello
```

It will give output like this:
```json
{
  "message": "hello"
}
```
 
## Getting Started

### Prerequisites
This program is not tested for python version smaller than 3.7, so you might need to install python version 3.7 or up to be able to run this.
You will also need git to clone this project from github
### Installing
#### Download project from github
First we need to clone the repository
```bash
git clone https://github.com/arfan/mockmania.git
```
and after that cd to that directory
```bash
cd mockmania
```

#### Create and activate virtual environment
You can use this commands to create python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Run the script
```
python main.py
```

If Mockmania cannot find suitable yaml file inside mocks folder, it will create it.
For example we can try to hit the api like this:
```bash
curl http://localhost:7000/not_exist_api
```

Mockmania will return output like this: 
```text
CHANGEME in file mocks/GET_not_exist_api_1583647044350.yaml
```

And if we look at mocks folder, we can find a new file like this `GET_not_exist_api_1583647044350.yaml`.
The content of the file is:
```yaml
method: GET
path: not_exist_api
response: CHANGEME in file mocks/GET_not_exist_api_1583647044350.yaml
```
We can then change the content to suit our need.


#### Run the sample use
Open another terminal and try this sample script that will call mockmania service,
It will use all features available in mockmania.
```
python sample_use.py
```

### Watch the demo here
You can also watch the demo of this in youtube (no sound)

[![Watch the video](https://img.youtube.com/vi/jEBp2gXIbSM/hqdefault.jpg)](https://youtu.be/jEBp2gXIbSM)


### Sample using postman collection 
Here is a sample api calls from postmant collection

[mockmania.postman_collection.json](mockmania.postman_collection.json)
