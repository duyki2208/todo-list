from locust import HttpUser, task, between, events
import random
from datetime import datetime
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TodoAppUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Initialize user data when starting"""
        self.todo_id = None
        self.todo_ids = []  # Store multiple todo IDs
        self.success_count = 0
        self.failure_count = 0
        
        # Login to get token
        login_data = {
            "email": f"test_user_{random.randint(1, 1000000)}@example.com",
            "password": "test123"
        }
        response = self.client.post("/auth/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            # If login fails, try to register
            register_data = {
                "email": login_data["email"],
                "password": login_data["password"],
                "name": f"Test User {random.randint(1, 1000000)}"
            }
            response = self.client.post("/auth/register", json=register_data)
            if response.status_code == 201:
                # Try login again after registration
                response = self.client.post("/auth/login", json=login_data)
                if response.status_code == 200:
                    self.token = response.json().get("token")
                    self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_all_todos(self):
        """Get all todos - higher weight (3) as this is a common operation"""
        with self.client.get("/api/tasks", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                self.success_count += 1
                # Store todo IDs for other operations
                try:
                    todos = response.json()
                    if todos:
                        self.todo_ids = [todo.get("id") for todo in todos]
                except:
                    pass
            else:
                self.failure_count += 1
                response.failure(f"Failed with status {response.status_code}")
    
    @task(2)
    def create_todo(self):
        """Create a new todo - medium weight (2)"""
        todo_data = {
            "text": f"Test Todo {random.randint(1, 1000)}",
            "date": datetime.now().isoformat(),
            "completed": False
        }
        with self.client.post("/api/tasks", json=todo_data, headers=self.headers, catch_response=True) as response:
            if response.status_code == 201:
                self.success_count += 1
                try:
                    self.todo_id = response.json().get("id")
                    if self.todo_id:
                        self.todo_ids.append(self.todo_id)
                except:
                    pass
            else:
                self.failure_count += 1
                response.failure(f"Failed with status {response.status_code}")
    
    @task(1)
    def get_single_todo(self):
        """Get a single todo - lower weight (1)"""
        if self.todo_ids:
            todo_id = random.choice(self.todo_ids)
            with self.client.get(f"/api/tasks/{todo_id}", headers=self.headers, catch_response=True) as response:
                if response.status_code == 200:
                    self.success_count += 1
                else:
                    self.failure_count += 1
                    response.failure(f"Failed with status {response.status_code}")
    
    @task(1)
    def update_todo(self):
        """Update a todo - lower weight (1)"""
        if self.todo_ids:
            todo_id = random.choice(self.todo_ids)
            update_data = {
                "text": f"Updated Todo {random.randint(1, 1000)}",
                "date": datetime.now().isoformat(),
                "completed": random.choice([True, False])
            }
            with self.client.put(f"/api/tasks/{todo_id}", json=update_data, headers=self.headers, catch_response=True) as response:
                if response.status_code == 200:
                    self.success_count += 1
                else:
                    self.failure_count += 1
                    response.failure(f"Failed with status {response.status_code}")
    
    @task(1)
    def delete_todo(self):
        """Delete a todo - lower weight (1)"""
        if self.todo_ids:
            todo_id = random.choice(self.todo_ids)
            with self.client.delete(f"/api/tasks/{todo_id}", headers=self.headers, catch_response=True) as response:
                if response.status_code == 200:
                    self.success_count += 1
                    self.todo_ids.remove(todo_id)
                else:
                    self.failure_count += 1
                    response.failure(f"Failed with status {response.status_code}")

    def on_stop(self):
        """Called when the user stops"""
        logger.info(f"User {self.user_id} completed with {self.success_count} successes and {self.failure_count} failures") 