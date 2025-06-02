from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pymongo import MongoClient, ReadPreference, WriteConcern
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import setup_logging

load_dotenv()

app = Flask(__name__)
CORS(app)

# Setup logging
logger = setup_logging('user_service')

# MongoDB connection with replica set
client = MongoClient(
    os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
    readPreference=ReadPreference.SECONDARY_PREFERRED,
    writeConcern=WriteConcern(w='majority')
)
db = client['todo_app']
users = db['users']

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

@app.route('/register', methods=['POST'])
def register():
    logger.info("POST /register request received")
    try:
        data = request.get_json()
        
        if users.find_one({'email': data['email']}):
            logger.warning(f"Email {data['email']} already exists")
            return jsonify({'error': 'Email already exists'}), 400
            
        user = {
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'name': data['name'],
            'created_at': datetime.utcnow()
        }
        
        users.insert_one(user)
        logger.info(f"User {data['email']} registered successfully")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    logger.info("POST /login request received")
    try:
        data = request.get_json()
        user = users.find_one({'email': data['email']})
        
        if not user or not check_password_hash(user['password'], data['password']):
            logger.warning(f"Invalid login attempt for {data['email']}")
            return jsonify({'error': 'Invalid credentials'}), 401
            
        payload = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        logger.info(f"User {data['email']} logged in successfully")
        return jsonify({'token': token})
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/users', methods=['GET'])
def get_users():
    logger.info("GET /users request received")
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("No token provided")
        return jsonify({'error': 'No token provided'}), 401
        
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_list = list(users.find({}, {'password': 0}))
        for user in user_list:
            user['_id'] = str(user['_id'])
        logger.info(f"Retrieved {len(user_list)} users")
        return jsonify(user_list)
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    logger.info("User Service starting...")
    app.run(host='0.0.0.0', port=5002) 