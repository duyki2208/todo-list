from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from datetime import datetime, timedelta
import os
import json
import logging
import traceback
from werkzeug.security import generate_password_hash, check_password_hash
from pupdb.core import PupDB
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# Cấu hình session
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),
    SESSION_REFRESH_EACH_REQUEST=True
)

# Cấu hình CORS
CORS(app, 
     supports_credentials=True,
     resources={r"/*": {
         "origins": "*",
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True
     }},
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type", "Authorization"],
     max_age=600)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Initialize PupDB with error handling
try:
    logger.info("Initializing databases...")
    users_db = PupDB('users.db')
    tasks_db = PupDB('tasks.db')
    
    # Initialize tasks database if empty
    if not tasks_db.get('tasks'):
        logger.info("Initializing empty tasks database")
        tasks_db.set('tasks', {})
        tasks_db.sync()
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")
    logger.error(traceback.format_exc())
    # Create new database files if they don't exist
    users_db = PupDB('users.db')
    tasks_db = PupDB('tasks.db')
    tasks_db.set('tasks', {})
    tasks_db.sync()

@app.before_request
def before_request():
    # Kiểm tra và khởi tạo lại database nếu cần
    try:
        if not tasks_db.get('tasks'):
            logger.info("Initializing empty tasks database")
            tasks_db.set('tasks', {})
            tasks_db.sync()
    except Exception as e:
        logger.error(f"Error in before_request: {str(e)}")
        logger.error(traceback.format_exc())

@app.teardown_appcontext
def teardown_appcontext(exception=None):
    # Đảm bảo dữ liệu được lưu trước khi đóng ứng dụng
    try:
        tasks_db.sync()
        users_db.sync()
    except Exception as e:
        logger.error(f"Error in teardown_appcontext: {str(e)}")
        logger.error(traceback.format_exc())

def get_user(email):
    try:
        user = users_db.get(email)
        if user and 'email' not in user:
            user['email'] = email
            save_user(email, user)
        return user
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return None

def save_user(email, user_data):
    try:
        users_db.set(email, user_data)
    except Exception as e:
        logger.error(f"Error saving user: {str(e)}")
        raise

def get_user_tasks(user_id):
    try:
        tasks = tasks_db.get('tasks', {})
        if not isinstance(tasks, dict):
            logger.warning("Tasks is not a dictionary, resetting to empty dict")
            tasks = {}
            tasks_db.set('tasks', tasks)
        return {task_id: task for task_id, task in tasks.items() 
                if task.get('user_id') == user_id}
    except Exception as e:
        logger.error(f"Error getting user tasks: {str(e)}")
        return {}

def save_task(task_id, task_data):
    try:
        tasks = tasks_db.get('tasks', {})
        if not isinstance(tasks, dict):
            logger.warning("Tasks is not a dictionary, resetting to empty dict")
            tasks = {}
        tasks[task_id] = task_data
        tasks_db.set('tasks', tasks)
        # Đảm bảo dữ liệu được lưu vào file
        tasks_db.sync()
    except Exception as e:
        logger.error(f"Error saving task: {str(e)}")
        raise

@app.route('/')
def index():
    logger.info(f"Index route accessed. Session: {session}")
    logger.info(f"Request headers: {request.headers}")
    
    if 'user_id' not in session:
        logger.warning("No user_id in session, redirecting to login")
        return redirect(url_for('login'))
    
    user = get_user(session['user_id'])
    if not user:
        logger.warning(f"User {session['user_id']} not found, clearing session")
        session.clear()
        return redirect(url_for('login'))
        
    logger.info(f"User {session['user_id']} accessing index page")
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info(f"Login route accessed. Method: {request.method}")
    logger.info(f"Current session: {session}")
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        logger.info(f"Login attempt for email: {email}")
        user = get_user(email)
        if user and check_password_hash(user['password'], password):
            # Không xóa session cũ, chỉ cập nhật user_id
            session['user_id'] = email
            session.permanent = True
            logger.info(f"User {email} logged in successfully. Session: {session}")
            
            # Tạo response với cookie session
            response = make_response(redirect(url_for('index')))
            response.set_cookie(
                'session',
                session.get('user_id'),
                httponly=True,
                samesite='Lax',
                max_age=2592000  # 30 ngày tính bằng giây
            )
            logger.info(f"Response headers: {response.headers}")
            return response
            
        logger.warning(f"Failed login attempt for email: {email}")
        return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        logger.info(f"Registration attempt for email: {email}")
        if get_user(email):
            logger.warning(f"Registration failed - Email already exists: {email}")
            return render_template('register.html', error='Email already exists')
        
        user_data = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password)
        }
        save_user(email, user_data)
        session['user_id'] = email
        logger.info(f"User {email} registered successfully")
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    logger.info(f"Logging out user. Session before logout: {session}")
    session.clear()
    logger.info("Session cleared")
    return redirect(url_for('login'))

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    logger.info(f"GET /api/tasks - Session: {session}")
    if 'user_id' not in session:
        logger.warning("Unauthorized access attempt to get_tasks")
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        logger.info(f"Fetching tasks for user: {session['user_id']}")
        tasks = tasks_db.get('tasks')
        logger.debug(f"Raw tasks from database: {tasks}")
        
        if not tasks:
            logger.info("No tasks found, returning empty object")
            return jsonify({})
            
        if not isinstance(tasks, dict):
            logger.warning("Tasks is not a dictionary, resetting to empty dict")
            tasks = {}
            tasks_db.set('tasks', tasks)
            
        user_tasks = {task_id: task for task_id, task in tasks.items() 
                     if task.get('user_id') == session['user_id']}
        logger.info(f"Found {len(user_tasks)} tasks for user")
        logger.debug(f"User tasks: {user_tasks}")
        
        return jsonify(user_tasks)
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    logger.info(f"POST /api/tasks - Session: {session}")
    if 'user_id' not in session:
        logger.warning("Unauthorized access attempt to add_task")
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        task = request.json
        logger.debug(f"Received task data: {task}")
        
        if not task:
            logger.warning("No task data received")
            return jsonify({'error': 'No task data provided'}), 400
            
        if 'text' not in task:
            logger.warning("No task text provided")
            return jsonify({'error': 'Task text is required'}), 400
            
        if 'date' not in task:
            logger.warning("No task date provided")
            return jsonify({'error': 'Task date is required'}), 400

        # Get current tasks
        try:
            tasks = tasks_db.get('tasks')
            if not isinstance(tasks, dict):
                logger.warning("Tasks is not a dictionary, resetting to empty dict")
                tasks = {}
        except Exception as e:
            logger.error(f"Error getting tasks from database: {str(e)}")
            tasks = {}

        # Generate task ID
        task_id = str(int(datetime.now().timestamp() * 1000))
        
        # Create task data
        task_data = {
            'id': task_id,
            'text': task['text'],
            'date': task['date'],
            'completed': task.get('completed', False),
            'user_id': session['user_id'],
            'timestamp': datetime.now().timestamp()
        }
        
        logger.info(f"Adding new task: {task_data}")
        
        # Add new task
        tasks[task_id] = task_data
        
        # Save to database
        try:
            tasks_db.set('tasks', tasks)
            # Đảm bảo dữ liệu được lưu vào file
            tasks_db.sync()
            logger.info("Task saved successfully")
            return jsonify(task_data)
        except Exception as e:
            logger.error(f"Error saving task to database: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Failed to save task to database'}), 500
            
    except Exception as e:
        logger.error(f"Error adding task: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to add task'}), 500

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        tasks = tasks_db.get('tasks', {})
        if task_id in tasks and tasks[task_id].get('user_id') == session['user_id']:
            task = request.json
            task['user_id'] = session['user_id']
            task['id'] = task_id  # Ensure ID is preserved
            tasks[task_id] = task
            tasks_db.set('tasks', tasks)
            return jsonify(task)
        return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to update task'}), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info(f"DELETE /api/tasks/{task_id} - Session: {session}")
    if 'user_id' not in session:
        logger.warning("Unauthorized access attempt to delete_task")
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get current tasks
        tasks = tasks_db.get('tasks')
        logger.debug(f"Current tasks: {tasks}")
        
        if not tasks:
            logger.warning("No tasks found in database")
            return jsonify({'error': 'No tasks found'}), 404
            
        if not isinstance(tasks, dict):
            logger.warning("Tasks is not a dictionary, resetting to empty dict")
            tasks = {}
            
        # Check if task exists and belongs to user
        if task_id not in tasks:
            logger.warning(f"Task {task_id} not found")
            return jsonify({'error': 'Task not found'}), 404
            
        if tasks[task_id].get('user_id') != session['user_id']:
            logger.warning(f"Task {task_id} does not belong to user {session['user_id']}")
            return jsonify({'error': 'Unauthorized'}), 401
            
        # Delete the task
        try:
            del tasks[task_id]
            tasks_db.set('tasks', tasks)
            logger.info(f"Task {task_id} deleted successfully")
            return jsonify({'message': 'Task deleted successfully'})
        except Exception as e:
            logger.error(f"Error saving tasks after deletion: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Failed to save changes'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to delete task'}), 500

@app.route('/health')
def health_check():
    return {"status": "healthy"}, 200

def backup_database():
    """Tạo bản sao lưu của database"""
    try:
        import shutil
        from datetime import datetime
        
        # Tạo thư mục backup nếu chưa tồn tại
        if not os.path.exists('backups'):
            os.makedirs('backups')
            
        # Tạo tên file backup với timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup tasks database
        if os.path.exists('tasks.db'):
            shutil.copy2('tasks.db', f'backups/tasks_{timestamp}.db')
            
        # Backup users database
        if os.path.exists('users.db'):
            shutil.copy2('users.db', f'backups/users_{timestamp}.db')
            
        logger.info(f"Database backup created at {timestamp}")
    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        logger.error(traceback.format_exc())

# Tạo backup khi khởi động ứng dụng
backup_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 