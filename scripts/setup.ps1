# OSINTGraph — setup Windows (PowerShell)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "OSINTGraph setup (Windows)" -ForegroundColor Cyan

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js 20+ requis. Installez-le depuis https://nodejs.org/"
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python 3.11+ requis."
}

Write-Host "npm install..."
npm install

$Backend = Join-Path $Root "backend"
Set-Location $Backend

if (-not (Test-Path ".venv")) {
    Write-Host "Creation venv Python..."
    python -m venv .venv
}

Write-Host "Installation dependances Python..."
& .\.venv\Scripts\pip install -r requirements.txt

Set-Location $Root

if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "backend\.env cree depuis .env.example"
}

if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
}

Write-Host ""
Write-Host "Pret. Lancez :" -ForegroundColor Green
Write-Host "  npm run dev           # React + API (http://localhost:5173)"
Write-Host "  npm run dev:streamlit # Preview Streamlit (http://localhost:8501)"
