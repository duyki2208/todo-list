from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Service URLs
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
TASK_SERVICE_URL = os.getenv('TASK_SERVICE_URL', 'http://localhost:5002')

@app.route('/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def auth_service(path):
    url = f'{AUTH_SERVICE_URL}/auth/{path}'
    response = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    return response.content, response.status_code, response.headers.items()

@app.route('/tasks/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def task_service(path):
    url = f'{TASK_SERVICE_URL}/tasks/{path}'
    response = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    return response.content, response.status_code, response.headers.items()

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    url = f'{TASK_SERVICE_URL}/tasks'
    response = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    return response.content, response.status_code, response.headers.items()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 