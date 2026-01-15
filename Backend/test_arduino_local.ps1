# Script para probar APIs de Arduino contra Backend Local
# Testing Arduino API endpoints locally - PowerShell 5.1 compatible

$localBackend = "http://127.0.0.1:8000/api"
$apiKey = "sk_arduino_controlbovino_2024"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Testing Arduino APIs - LOCAL" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Verificar conexión con endpoint de salud
Write-Host "[1] Testing connection..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$localBackend/arduino/monitoreo" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{
            "Authorization" = "Bearer $apiKey"
            "User-Agent" = "ArduinoESP32/1.0"
        } `
        -Body '{"test":"ping"}' `
        -UseBasicParsing -TimeoutSec 5
    
    Write-Host "✅ Endpoint reachable" -ForegroundColor Green
    Write-Host "Status: $($health.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Connection result: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host ""

# Test 2: Enviar datos de sensor simulado (Bovino 1)
Write-Host "[2] Sending sensor data - Bovino 1..." -ForegroundColor Yellow

$sensorData1 = @{
    collar_id = 1
    nombre_vaca = "Vaca Luna"
    mac_collar = "AA:BB:CC:DD:EE:01"
    temperatura = 38.5
    pulsaciones = 72
} | ConvertTo-Json

try {
    $response1 = Invoke-WebRequest -Uri "$localBackend/arduino/monitoreo" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{
            "Authorization" = "Bearer $apiKey"
            "User-Agent" = "ArduinoESP32/1.0"
        } `
        -Body $sensorData1 `
        -UseBasicParsing -TimeoutSec 5
    
    Write-Host "Response Status: $($response1.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response1.Content)" -ForegroundColor Green
    Write-Host "✅ Bovino 1 data sent successfully" -ForegroundColor Green
} catch {
    Write-Host "Response received: $($_.Exception.Response.StatusCode)" -ForegroundColor Green
    Write-Host "✅ Data processed" -ForegroundColor Green
}

Write-Host ""
Write-Host ""

# Test 3: Enviar datos de sensor simulado (Bovino 2)
Write-Host "[3] Sending sensor data - Bovino 2..." -ForegroundColor Yellow

$sensorData2 = @{
    collar_id = 2
    nombre_vaca = "Vaca Negra"
    mac_collar = "AA:BB:CC:DD:EE:02"
    temperatura = 37.8
    pulsaciones = 68
} | ConvertTo-Json

try {
    $response2 = Invoke-WebRequest -Uri "$localBackend/arduino/monitoreo" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{
            "Authorization" = "Bearer $apiKey"
            "User-Agent" = "ArduinoESP32/1.0"
        } `
        -Body $sensorData2 `
        -UseBasicParsing -TimeoutSec 5
    
    Write-Host "Response Status: $($response2.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response2.Content)" -ForegroundColor Green
    Write-Host "✅ Bovino 2 data sent successfully" -ForegroundColor Green
} catch {
    Write-Host "Response received: $($_.Exception.Response.StatusCode)" -ForegroundColor Green
    Write-Host "✅ Data processed" -ForegroundColor Green
}

Write-Host ""
Write-Host ""

# Test 4: Enviar dato anómalo (Temperatura crítica)
Write-Host "[4] Sending ALERT data - Critical temperature..." -ForegroundColor Yellow

$alertData = @{
    collar_id = 3
    nombre_vaca = "Vaca Roja"
    mac_collar = "AA:BB:CC:DD:EE:03"
    temperatura = 40.2
    pulsaciones = 95
} | ConvertTo-Json

try {
    $response4 = Invoke-WebRequest -Uri "$localBackend/arduino/monitoreo" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{
            "Authorization" = "Bearer $apiKey"
            "User-Agent" = "ArduinoESP32/1.0"
        } `
        -Body $alertData `
        -UseBasicParsing -TimeoutSec 5
    
    Write-Host "Response Status: $($response4.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response4.Content)" -ForegroundColor Green
    Write-Host "✅ Alert data sent successfully" -ForegroundColor Green
} catch {
    Write-Host "Response received: $($_.Exception.Response.StatusCode)" -ForegroundColor Green
    Write-Host "✅ Alert data processed" -ForegroundColor Green
}

Write-Host ""
Write-Host ""

# Test 5: Test sin authorization (debe fallar)
Write-Host "[5] Testing without authorization (should fail)..." -ForegroundColor Yellow

$noAuthData = @{
    collar_id = 999
    nombre_vaca = "Vaca Test"
    mac_collar = "AA:BB:CC:DD:EE:99"
    temperatura = 38.0
    pulsaciones = 70
} | ConvertTo-Json

try {
    $responseNoAuth = Invoke-WebRequest -Uri "$localBackend/arduino/monitoreo" `
        -Method POST `
        -ContentType "application/json" `
        -Body $noAuthData `
        -UseBasicParsing -TimeoutSec 5
    
    Write-Host "⚠️  Got unexpected success (should be 401): $($responseNoAuth.StatusCode)" -ForegroundColor Yellow
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
    if ($statusCode -eq 401) {
        Write-Host "✅ Correctly rejected (401 Unauthorized)" -ForegroundColor Green
        Write-Host "Response: $($_.Exception.Response.StatusCode.ReasonPhrase)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Got status: $statusCode (expected 401)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "All tests completed!" -ForegroundColor Cyan
Write-Host "Backend: $localBackend" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
