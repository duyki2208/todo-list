FROM python:3.9-slim

WORKDIR /app

# Cài đặt các package cơ bản
RUN pip install --no-cache-dir Flask==2.0.1 \
    Werkzeug==2.0.1 \
    Jinja2==3.0.1 \
    MarkupSafe==2.0.1 \
    itsdangerous==2.0.1 \
    click==8.0.1 \
    python-dotenv==0.19.0 \
    requests==2.31.0 \
    flask-cors==4.0.0

# Cài đặt pupdb riêng
RUN pip install --no-cache-dir pupdb==0.1.4

# Copy file app.py
COPY services/task_service/app.py .

CMD ["python", "app.py"] 