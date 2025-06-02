# Create necessary directories
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs"
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    @"
# MongoDB Configuration
MONGODB_URI=mongodb://mongodb-primary:27017,mongodb-secondary-1:27017,mongodb-secondary-2:27017/?replicaSet=rs0

# Service URLs
TASK_SERVICE_URL=http://task_service:5001
USER_SERVICE_URL=http://user_service:5002
AUTH_SERVICE_URL=http://auth_service:5003

# JWT Configuration
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

# Build and start services
Write-Host "Building and starting services..."
docker-compose build
docker-compose up -d

# Wait for services to start
Write-Host "Waiting for services to start..."
Start-Sleep -Seconds 10

# Check service health
Write-Host "Checking service health..."
$services = @("api_service", "task_service", "user_service", "auth_service")
foreach ($service in $services) {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
    if ($health.status -eq "healthy") {
        Write-Host "$service is healthy"
    } else {
        Write-Host "$service is not healthy"
    }
}

Write-Host "Setup completed!" 