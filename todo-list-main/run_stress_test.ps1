# Try to kill any existing locust processes, but don't fail if none found
try {
    Get-Process -Name "python" | Where-Object {$_.CommandLine -like "*locust*"} | Stop-Process -Force
} catch {
    Write-Host "No existing locust processes found"
}

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs"
}

# Start MongoDB monitoring in background
$mongodbLog = "logs/mongodb_stats.log"
Start-Process -NoNewWindow -FilePath "mongosh" -ArgumentList "mongodb://localhost:27017 --eval 'db.serverStatus()'" -RedirectStandardOutput $mongodbLog

# Start service monitoring
$serviceLogs = @{
    "api_service" = "logs/api_service.log"
    "task_service" = "logs/task_service.log"
    "user_service" = "logs/user_service.log"
}

foreach ($service in $serviceLogs.Keys) {
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-c `"import logging; logging.basicConfig(filename='$($serviceLogs[$service])', level=logging.INFO); logging.info('Starting $service monitoring')`""
}

# Start locust in headless mode
$env:PYTHONUNBUFFERED=1
python -m locust -f locustfile.py `
    --host http://localhost:5000 `
    --users 100 `
    --spawn-rate 10 `
    --run-time 5m `
    --headless `
    --only-summary `
    --logfile logs/stress_test_results.log

# Print results
Write-Host "`nStress Test Results:"
Write-Host "==================="
Get-Content logs/stress_test_results.log

# Print MongoDB stats
Write-Host "`nMongoDB Statistics:"
Write-Host "==================="
Get-Content $mongodbLog

# Print service logs
Write-Host "`nService Logs:"
Write-Host "============="
foreach ($service in $serviceLogs.Keys) {
    Write-Host "`n$service Log:"
    Write-Host "-------------"
    Get-Content $serviceLogs[$service]
}

# Monitor system resources
Write-Host "`nSystem Resources:"
Write-Host "================="
Get-Counter '\Processor(_Total)\% Processor Time', '\Memory\Available MBytes', '\PhysicalDisk(_Total)\% Disk Time' -SampleInterval 1 -MaxSamples 1 | Format-Table -AutoSize 