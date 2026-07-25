$ErrorActionPreference = "Stop"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
docker compose up -d --build
Write-Host ""
Write-Host "SitePulse iniciado:" -ForegroundColor Green
Write-Host "Dashboard  http://localhost:3000"
Write-Host "Swagger    http://localhost:8000/docs"
Write-Host "Mailpit    http://localhost:8025"
Write-Host "Flower     http://localhost:5555"
Write-Host "Demo       http://localhost:8080/product"
