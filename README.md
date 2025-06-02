# Python To-Do List Application

A modern To-Do List application built with Python Flask and modern web technologies.

## Features

- Add, edit, and delete tasks
- Set due dates for tasks
- Filter tasks by day, week, or month
- Search functionality
- Responsive design for mobile devices
- Modern and clean user interface
- Persistent storage using JSON file

## Requirements

- Python 3.7 or higher
- Flask 2.0.1
- Modern web browser

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd todo_app
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

- Windows:

```bash
venv\Scripts\activate
```

- Linux/Mac:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5000
```

## Usage

1. Add a new task:

   - Enter task description in the text field
   - Select a due date
   - Click the plus icon or press Enter

2. Mark a task as complete:

   - Click the checkbox next to the task

3. Delete a task:

   - Click the trash icon next to the task
   - Confirm deletion in the popup

4. Filter tasks:

   - Click on "My day" to see today's tasks
   - Click on "This week" to see this week's tasks
   - Click on "This month" to see this month's tasks
   - Click on "All tasks" to see all tasks

5. Search tasks:
   - Use the search bar in the left sidebar
   - Press Enter to search

## Project Structure

```
todo_app/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── img/
│       ├── profile.png
│       └── ico.png
├── templates/
│   └── index.html
├── app.py
└── requirements.txt
```

## Contributing

Feel free to submit issues and enhancement requests!
