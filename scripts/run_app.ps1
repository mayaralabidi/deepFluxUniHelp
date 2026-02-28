# Run DeepFluxUniHelp: API + Frontend
# Usage: .\scripts\run_app.ps1
# Or run in two separate terminals (see below).

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location $root

# Check venv
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Create venv first: python -m venv .venv" -ForegroundColor Red
    exit 1
}

Write-Host "Starting API on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath ".venv\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"
Start-Sleep -Seconds 2

Write-Host "Starting Streamlit on http://localhost:8501 ..." -ForegroundColor Cyan
& .venv\Scripts\streamlit.exe run frontend/app_new.py --server.headless true
