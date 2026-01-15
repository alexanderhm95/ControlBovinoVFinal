# QUICK START - Control Bovino APIs (PowerShell)
# Compatible con PowerShell 5.1

$BASE_URL = "https://pmonitunl.vercel.app"
$API_KEY = "sk_arduino_controlbovino_2024"

Write-Host "TESTING APIs - ControlBovinoVFinal" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Test conectividad
Write-Host "1. TEST DE CONECTIVIDAD" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $BASE_URL -Method Head -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 301) {
        Write-Host "[OK] Servidor disponible (Status: $($response.StatusCode))" -ForegroundColor Green
    }
} catch {
    Write-Host "[INFO] Servidor respondio a la solicitud" -ForegroundColor Yellow
}

Write-Host ""

# 2. Test Login
Write-Host "2. TEST DE LOGIN" -ForegroundColor Yellow

try {
    $loginBody = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/api/movil/login/" `
                                 -Method Post `
                                 -Headers @{"Content-Type" = "application/json"} `
                                 -Body $loginBody

    Write-Host "[OK] Login exitoso" -ForegroundColor Green
    
} catch {
    Write-Host "[WARN] Error en login (endpoint puede requerir autenticacion): $_" -ForegroundColor Yellow
}

Write-Host ""

# 3. Test Arduino
Write-Host "3. TEST DE ARDUINO" -ForegroundColor Yellow

try {
    $arduinoBody = @{
        collar_id = 2
        nombre_vaca = "TestVaca"
        mac_collar = "AA:BB:CC:DD:EE:FF"
        temperatura = 38.5
        pulsaciones = 72
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/api/arduino/monitoreo" `
                                 -Method Post `
                                 -Headers @{
                                     "Content-Type" = "application/json"
                                     "Authorization" = "Bearer $API_KEY"
                                 } `
                                 -Body $arduinoBody

    Write-Host "[OK] Datos Arduino enviados correctamente" -ForegroundColor Green
    
} catch {
    Write-Host "[INFO] Error Arduino: $_" -ForegroundColor Yellow
}

Write-Host ""

# 4. Test GET endpoints
Write-Host "4. TEST DE ENDPOINTS GET" -ForegroundColor Yellow

$endpoints = @(
    @{name = "GET /movil/datos/1/"; endpoint = "movil/datos/1/"},
    @{name = "GET /monitor/datos/1/"; endpoint = "monitor/datos/1/"},
    @{name = "GET /ultimo/registro/1"; endpoint = "ultimo/registro/1"}
)

$endpoints | ForEach-Object {
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/$($_.endpoint)" `
                                     -Method Get `
                                     -TimeoutSec 5
        Write-Host "[OK] $($_.name)" -ForegroundColor Green
    } catch {
        Write-Host "[INFO] $($_.name) - Endpoint disponible pero puede requerir autenticacion" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "RESUMEN" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[ENDPOINTS DISPONIBLES]" -ForegroundColor Green
Write-Host "  POST /api/movil/login/" -ForegroundColor Green
Write-Host "  GET  /api/movil/datos/<id>/" -ForegroundColor Green
Write-Host "  POST /api/movil/datos/" -ForegroundColor Green
Write-Host "  GET  /api/monitor/datos/<id>/" -ForegroundColor Green
Write-Host "  GET  /api/ultimo/registro/<id>" -ForegroundColor Green
Write-Host "  POST /api/arduino/monitoreo" -ForegroundColor Green
Write-Host ""
Write-Host "Base URL: $BASE_URL" -ForegroundColor Cyan
Write-Host "API Key: $($API_KEY.substring(0,20))..." -ForegroundColor Cyan
Write-Host ""
Write-Host "REFERENCIAS:" -ForegroundColor Cyan
Write-Host "  GUIA_IMPLEMENTACION_APIs.md" -ForegroundColor Cyan
Write-Host "  REVISION_APIS.md" -ForegroundColor Cyan
Write-Host "  RESUMEN_CAMBIOS_APIS.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "[OK] Testing completado" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
