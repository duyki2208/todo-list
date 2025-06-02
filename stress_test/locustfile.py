from locust import HttpUser, task, between
import random
import json

class TodoAppUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    token = None
    user_id = None

    def on_start(self):
        """Initialize user session"""
        # Register a new user
        email = f"test_user_{random.randint(1, 1000000)}@example.com"
        password = "test_password"
        name = f"Test User {random.randint(1, 1000000)}"

        response = self.client.post(
            "/api/register",
            json={
                "email": email,
                "password": password,
                "name": name
            }
        )

        if response.status_code == 201:
            # Login to get token
            response = self.client.post(
                "/api/login",
                json={
                    "email": email,
                    "password": password
                }
            )
            if response.status_code == 200:
                self.token = response.json()["token"]
                self.user_id = email

    @task(3)
    def get_tasks(self):
        """Get all tasks"""
        if not self.token:
            return

        self.client.get(
            "/api/tasks",
            headers={"Authorization": self.token}
        )

    @task(2)
    def create_task(self):
        """Create a new task"""
        if not self.token:
            return

        task_data = {
            "text": f"Test task {random.randint(1, 1000000)}",
            "date": "2024-03-14",
            "completed": False
        }

        self.client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": self.token}
        )

    @task(1)
    def update_task(self):
        """Update a random task"""
        if not self.token:
            return

        # First get all tasks
        response = self.client.get(
            "/api/tasks",
            headers={"Authorization": self.token}
        )

        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                task = random.choice(tasks)
                task_id = task["_id"]
                
                # Update the task
                update_data = {
                    "text": f"Updated task {random.randint(1, 1000000)}",
                    "completed": not task.get("completed", False)
                }

                self.client.put(
                    f"/api/tasks/{task_id}",
                    json=update_data,
                    headers={"Authorization": self.token}
                )

    @task(1)
    def delete_task(self):
        """Delete a random task"""
        if not self.token:
            return

        # First get all tasks
        response = self.client.get(
            "/api/tasks",
            headers={"Authorization": self.token}
        )

        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                task = random.choice(tasks)
                task_id = task["_id"]
                
                self.client.delete(
                    f"/api/tasks/{task_id}",
                    headers={"Authorization": self.token}
                ) 