from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from pymongo import MongoClient, ReadPreference, WriteConcern
import jwt
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import setup_logging

load_dotenv()

app = Flask(__name__)
CORS(app)

# Setup logging
logger = setup_logging('task_service')

# MongoDB connection with replica set
client = MongoClient(
    os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
    readPreference=ReadPreference.SECONDARY_PREFERRED,
    writeConcern=WriteConcern(w='majority')
)
db = client['todo_app']
tasks = db['tasks']

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

@app.route('/tasks', methods=['GET'])
def get_tasks():
    logger.info("GET /tasks request received")
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("No token provided")
        return jsonify({'error': 'No token provided'}), 401
        
    payload = verify_token(token)
    if not payload:
        logger.warning("Invalid token")
        return jsonify({'error': 'Invalid token'}), 401
        
    try:
        user_tasks = list(tasks.find({'user_id': payload['user_id']}))
        for task in user_tasks:
            task['_id'] = str(task['_id'])
        logger.info(f"Retrieved {len(user_tasks)} tasks for user {payload['user_id']}")
        return jsonify(user_tasks)
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/tasks', methods=['POST'])
def create_task():
    logger.info("POST /tasks request received")
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("No token provided")
        return jsonify({'error': 'No token provided'}), 401
        
    payload = verify_token(token)
    if not payload:
        logger.warning("Invalid token")
        return jsonify({'error': 'Invalid token'}), 401
        
    try:
        task = request.json
        task['user_id'] = payload['user_id']
        task['created_at'] = datetime.utcnow()
        
        result = tasks.insert_one(task)
        task['_id'] = str(result.inserted_id)
        logger.info(f"Created new task for user {payload['user_id']}")
        return jsonify(task), 201
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    logger.info(f"PUT /tasks/{task_id} request received")
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("No token provided")
        return jsonify({'error': 'No token provided'}), 401
        
    payload = verify_token(token)
    if not payload:
        logger.warning("Invalid token")
        return jsonify({'error': 'Invalid token'}), 401
        
    try:
        task = request.json
        task['user_id'] = payload['user_id']
        task['updated_at'] = datetime.utcnow()
        
        result = tasks.update_one(
            {'_id': task_id, 'user_id': payload['user_id']},
            {'$set': task}
        )
        
        if result.modified_count == 0:
            logger.warning(f"Task {task_id} not found for user {payload['user_id']}")
            return jsonify({'error': 'Task not found'}), 404
            
        logger.info(f"Updated task {task_id} for user {payload['user_id']}")
        return jsonify({'message': 'Task updated successfully'})
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info(f"DELETE /tasks/{task_id} request received")
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("No token provided")
        return jsonify({'error': 'No token provided'}), 401
        
    payload = verify_token(token)
    if not payload:
        logger.warning("Invalid token")
        return jsonify({'error': 'Invalid token'}), 401
        
    try:
        result = tasks.delete_one({'_id': task_id, 'user_id': payload['user_id']})
        if result.deleted_count == 0:
            logger.warning(f"Task {task_id} not found for user {payload['user_id']}")
            return jsonify({'error': 'Task not found'}), 404
            
        logger.info(f"Deleted task {task_id} for user {payload['user_id']}")
        return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Task Service starting...")
    app.run(host='0.0.0.0', port=5001) 