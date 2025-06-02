from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)  # Thêm secret key cho session

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Service URLs
TASK_SERVICE_URL = os.getenv('TASK_SERVICE_URL', 'http://localhost:5001')
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5002')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        response = requests.post(f'{USER_SERVICE_URL}/login', json=data)
        if response.status_code == 200:
            session['user_id'] = data.get('email')
            return jsonify(response.json()), 200
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        response = requests.post(f'{USER_SERVICE_URL}/register', json=data)
        if response.status_code == 201:
            session['user_id'] = data.get('email')
            return jsonify(response.json()), 201
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        response = requests.get(f'{TASK_SERVICE_URL}/tasks')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.json
        data['user_id'] = session['user_id']
        response = requests.post(f'{TASK_SERVICE_URL}/tasks', json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.json
        data['user_id'] = session['user_id']
        response = requests.put(f'{TASK_SERVICE_URL}/tasks/{task_id}', json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        response = requests.delete(f'{TASK_SERVICE_URL}/tasks/{task_id}')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        response = requests.get(f'{USER_SERVICE_URL}/users')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        response = requests.post(f'{USER_SERVICE_URL}/users', json=request.json)
        if response.status_code == 201:
            session['user_id'] = request.json.get('email')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 