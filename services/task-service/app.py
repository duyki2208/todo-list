from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import jwt

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client['todo_app']
tasks = db['tasks']

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except:
        return None

@app.route('/tasks', methods=['GET'])
def get_tasks():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401
        
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
        
    user_tasks = list(tasks.find({'user_id': payload['user_id']}))
    for task in user_tasks:
        task['_id'] = str(task['_id'])
    return jsonify(user_tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401
        
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
        
    data = request.get_json()
    task = {
        'text': data['text'],
        'date': data['date'],
        'completed': data.get('completed', False),
        'user_id': payload['user_id'],
        'created_at': datetime.utcnow()
    }
    
    result = tasks.insert_one(task)
    task['_id'] = str(result.inserted_id)
    return jsonify(task), 201

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401
        
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
        
    task = tasks.find_one({'_id': task_id, 'user_id': payload['user_id']})
    if not task:
        return jsonify({'error': 'Task not found'}), 404
        
    data = request.get_json()
    update_data = {
        'text': data.get('text', task['text']),
        'date': data.get('date', task['date']),
        'completed': data.get('completed', task['completed'])
    }
    
    tasks.update_one({'_id': task_id}, {'$set': update_data})
    task.update(update_data)
    task['_id'] = str(task['_id'])
    return jsonify(task)

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401
        
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
        
    result = tasks.delete_one({'_id': task_id, 'user_id': payload['user_id']})
    if result.deleted_count == 0:
        return jsonify({'error': 'Task not found'}), 404
        
    return jsonify({'message': 'Task deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002) 