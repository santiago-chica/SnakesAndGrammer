$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start-backend.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start-frontend.ps1"
Write-Host "Backend + frontend started."
Write-Host "Open http://localhost:5500"
