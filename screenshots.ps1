# PowerShell script to capture screenshots for demo

Write-Host "Capturing screenshots for demo documentation..." -ForegroundColor Green

# Screenshot 1: Frontend main page
Start-Sleep -Seconds 2
Start-Process "http://localhost"
Start-Sleep -Seconds 3
# Manual: Press Win+Shift+S to capture

Write-Host ""
Write-Host "Please capture the following screenshots:" -ForegroundColor Yellow
Write-Host "1. Frontend main page (http://localhost)"
Write-Host "2. Creating a delivery"
Write-Host "3. Tracking status update"
Write-Host "4. Notifications list"
Write-Host "5. API endpoints (Swagger or curl responses)"
Write-Host "6. Docker containers running (docker-compose ps)"
Write-Host "7. Test results (python run_tests.py)"
Write-Host "8. Logs (logs/delivery_app.log)"
Write-Host ""
Write-Host "Screenshots saved to: screenshots/"
