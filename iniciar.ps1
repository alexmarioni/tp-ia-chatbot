# iniciar.ps1 - Levanta backend + frontend del chatbot de clima
$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Chatbot de Clima - Lanzador"

$root       = $PSScriptRoot
$backendDir = Join-Path $root "backend"
$venvDir    = Join-Path $backendDir ".venv"
$envFile    = Join-Path $backendDir ".env"
$reqs       = Join-Path $backendDir "requirements.txt"
$activate   = Join-Path $venvDir "Scripts\Activate.ps1"
$exePath    = Join-Path $root "flutter_app\build\windows\x64\runner\Release\chatbot_clima.exe"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Chatbot de Clima - Lanzador          " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar .env
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] No se encontro backend\.env" -ForegroundColor Red
    Write-Host "        Crea el archivo con: GROQ_API_KEY=gsk_..." -ForegroundColor Yellow
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

# 3. Crear venv si no existe
if (-not (Test-Path $venvDir)) {
    Write-Host "[...] Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv $venvDir
    Write-Host "[OK] Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "[OK] Entorno virtual existente" -ForegroundColor Green
}

# 4. Activar e instalar dependencias
& $activate
Write-Host "[...] Verificando dependencias..." -ForegroundColor Yellow
pip install -r $reqs -q --disable-pip-version-check
Write-Host "[OK] Dependencias listas" -ForegroundColor Green

# 5. Verificar / buildear Flutter EXE
if (-not (Test-Path $exePath)) {
    Write-Host ""
    Write-Host "[!] EXE de Flutter no encontrado." -ForegroundColor Yellow
    $flutterCmd = Get-Command flutter -ErrorAction SilentlyContinue
    if ($null -eq $flutterCmd) {
        Write-Host "[ERROR] flutter.exe no esta en PATH y el EXE no existe." -ForegroundColor Red
        Write-Host "        Ejecuta manualmente: cd flutter_app && flutter build windows --release" -ForegroundColor Yellow
        Read-Host "Presiona Enter para salir"
        exit 1
    }
    Write-Host "[...] Buildeando Flutter (puede tardar 2-3 minutos)..." -ForegroundColor Yellow
    Write-Host "      No cierres esta ventana." -ForegroundColor Gray
    Push-Location (Join-Path $root "flutter_app")
    flutter build windows --release
    $buildCode = $LASTEXITCODE
    Pop-Location
    if ($buildCode -ne 0) {
        Write-Host "[ERROR] El build de Flutter fallo (codigo $buildCode)." -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
    Write-Host "[OK] Build de Flutter completado" -ForegroundColor Green
} else {
    Write-Host "[OK] EXE de Flutter encontrado" -ForegroundColor Green
}

# 6. Arrancar backend en nueva ventana (no bloqueante)
Write-Host ""
Write-Host "[...] Iniciando backend en ventana separada..." -ForegroundColor Yellow
$backendCmd = "& '$activate'; Set-Location '$backendDir'; uvicorn main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal
Write-Host "[OK] Backend lanzado" -ForegroundColor Green

# 7. Esperar que uvicorn arranque y lanzar Flutter
Write-Host "[...] Esperando que el servidor arranque (3 seg)..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "[OK] Lanzando aplicacion Flutter..." -ForegroundColor Green
Start-Process $exePath

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host " Backend:  http://localhost:8000         " -ForegroundColor Green
Write-Host " Docs API: http://localhost:8000/docs    " -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "Este script puede cerrarse. El backend y la app siguen corriendo." -ForegroundColor Gray
Write-Host ""
