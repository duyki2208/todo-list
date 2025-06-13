# Cấu hình cơ bản
$baseUrl = "http://localhost:5000"
$headers = @{
    "Content-Type" = "application/json"
}

# Biến lưu trữ session cookie
$sessionCookie = $null

# Hàm đăng ký
function Register-User {
    param (
        [string]$name,
        [string]$email,
        [string]$password
    )
    
    $body = @{
        "name" = $name
        "email" = $email
        "password" = $password
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/api/register" -Method Post -Headers $headers -Body $body -SessionVariable session
    $script:sessionCookie = $session
    return $response
}

# Hàm đăng nhập
function Login-User {
    param (
        [string]$email,
        [string]$password
    )
    
    $body = @{
        "email" = $email
        "password" = $password
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/api/login" -Method Post -Headers $headers -Body $body -SessionVariable session
    $script:sessionCookie = $session
    return $response
}

# Hàm tạo task
function New-Task {
    param (
        [string]$title,
        [string]$description
    )
    
    if (-not $sessionCookie) {
        Write-Error "Chưa đăng nhập. Vui lòng đăng nhập trước."
        return
    }

    $body = @{
        "title" = $title
        "description" = $description
    } | ConvertTo-Json

    return Invoke-RestMethod -Uri "$baseUrl/api/tasks" -Method Post -Headers $headers -Body $body -WebSession $sessionCookie
}

# Hàm lấy danh sách tasks
function Get-Tasks {
    if (-not $sessionCookie) {
        Write-Error "Chưa đăng nhập. Vui lòng đăng nhập trước."
        return
    }

    return Invoke-RestMethod -Uri "$baseUrl/api/tasks" -Method Get -Headers $headers -WebSession $sessionCookie
}

# Hàm đăng xuất
function Logout-User {
    if (-not $sessionCookie) {
        Write-Error "Chưa đăng nhập. Vui lòng đăng nhập trước."
        return
    }

    $response = Invoke-RestMethod -Uri "$baseUrl/api/logout" -Method Post -Headers $headers -WebSession $sessionCookie
    $script:sessionCookie = $null
    return $response
}

# Ví dụ sử dụng:
Write-Host "1. Đăng ký tài khoản mới"
$registerResponse = Register-User -name "Test User" -email "test@example.com" -password "password123"
Write-Host "Đăng ký thành công: $($registerResponse | ConvertTo-Json)"

Write-Host "`n2. Đăng nhập"
$loginResponse = Login-User -email "test@example.com" -password "password123"
Write-Host "Đăng nhập thành công: $($loginResponse | ConvertTo-Json)"

Write-Host "`n3. Tạo task mới"
$taskResponse = New-Task -title "Test Task" -description "This is a test task"
Write-Host "Tạo task thành công: $($taskResponse | ConvertTo-Json)"

Write-Host "`n4. Lấy danh sách tasks"
$tasks = Get-Tasks
Write-Host "Danh sách tasks: $($tasks | ConvertTo-Json)"

Write-Host "`n5. Đăng xuất"
$logoutResponse = Logout-User
Write-Host "Đăng xuất thành công: $($logoutResponse | ConvertTo-Json)" 