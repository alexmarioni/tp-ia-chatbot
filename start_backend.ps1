# start_backend.ps1 — Levanta el backend del chatbot de clima
$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Chatbot de Clima — Backend"

$root       = $PSScriptRoot
$backendDir = Join-Path $root "backend"
$venvDir    = Join-Path $backendDir ".venv"
$envFile    = Join-Path $backendDir ".env"
$reqs       = Join-Path $backendDir "requirements.txt"
$activate   = Join-Path $venvDir "Scripts\Activate.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Chatbot de Clima — Backend Launcher  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar .env
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] No se encontro backend\.env" -ForegroundColor Red
    Write-Host "        Crea el archivo con tu GROQ_API_KEY:" -ForegroundColor Yellow
    Write-Host "        GROQ_API_KEY=gsk_..." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "[OK] .env encontrado" -ForegroundColor Green

# 2. Verificar Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "[OK] $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no encontrado. Instala Python 3.10+ desde https://python.org" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# 3. Crear entorno virtual si no existe
if (-not (Test-Path $venvDir)) {
    Write-Host "[...] Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv $venvDir
    Write-Host "[OK] Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "[OK] Entorno virtual existente" -ForegroundColor Green
}

# 4. Activar entorno virtual
& $activate

# 5. Instalar / actualizar dependencias
Write-Host "[...] Verificando dependencias..." -ForegroundColor Yellow
pip install -r $reqs -q --disable-pip-version-check
Write-Host "[OK] Dependencias listas" -ForegroundColor Green

# 6. Iniciar servidor
Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host " Backend corriendo en http://localhost:8000" -ForegroundColor Green
Write-Host " Docs:            http://localhost:8000/docs" -ForegroundColor Green
Write-Host " Ctrl+C para detener" -ForegroundColor Gray
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host ""

Set-Location $backendDir
uvicorn main:app --reload --host 0.0.0.0 --port 8000
