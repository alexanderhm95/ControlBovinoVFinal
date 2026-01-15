# Script para probar múltiples escenarios de salud de las vacas
$baseUrl = "http://127.0.0.1:8000/api/arduino/monitoreo"
$apiKey = "sk_arduino_controlbovino_2024"

# Función para hacer POST request
function Send-ArduinoData {
    param(
        [int]$collar_id,
        [string]$nombre_vaca,
        [string]$mac_collar,
        [double]$temperatura,
        [int]$pulsaciones,
        [string]$escenario
    )
    
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "Content-Type"  = "application/json"
    }
    
    $body = @{
        collar_id    = $collar_id
        nombre_vaca  = $nombre_vaca
        mac_collar   = $mac_collar
        temperatura  = $temperatura
        pulsaciones  = $pulsaciones
    } | ConvertTo-Json
    
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "Escenario: $escenario" -ForegroundColor Yellow
    Write-Host "Collar: $nombre_vaca (ID: $collar_id)" -ForegroundColor Green
    Write-Host "Temperatura: ${temperatura}C | Pulsaciones: $pulsaciones BPM" -ForegroundColor Magenta
    
    try {
        $response = Invoke-RestMethod -Uri $baseUrl -Method POST -Headers $headers -Body $body
        
        $statusColor = "Green"
        if ($response.estado_salud -eq "Alerta") { $statusColor = "Yellow" }
        if ($response.estado_salud -eq "Crítico") { $statusColor = "Red" }
        
        Write-Host "Estado de Salud: $($response.estado_salud)" -ForegroundColor $statusColor
        Write-Host "ID: $($response.id)" -ForegroundColor Cyan
        Write-Host "Respuesta: 201 Created OK" -ForegroundColor Green
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# PRUEBAS
Write-Host "`n==== PRUEBAS DE SALUD - 3 ESCENARIOS ====" -ForegroundColor Cyan

Write-Host "`n--- ESTADO NORMAL (36-39C) ---" -ForegroundColor Green
Send-ArduinoData -collar_id 1 -nombre_vaca "Marta" -mac_collar "AA:BB:CC:DD:EE:01" -temperatura 37.2 -pulsaciones 65 -escenario "Vaca Sana 1"
Send-ArduinoData -collar_id 2 -nombre_vaca "Rosa" -mac_collar "AA:BB:CC:DD:EE:02" -temperatura 38.1 -pulsaciones 72 -escenario "Vaca Sana 2"
Send-ArduinoData -collar_id 3 -nombre_vaca "Bella" -mac_collar "AA:BB:CC:DD:EE:03" -temperatura 36.5 -pulsaciones 58 -escenario "Vaca Sana 3"

Write-Host "`n--- ESTADO ALERTA (39-40C) ---" -ForegroundColor Yellow
Send-ArduinoData -collar_id 4 -nombre_vaca "Paloma" -mac_collar "AA:BB:CC:DD:EE:04" -temperatura 39.2 -pulsaciones 85 -escenario "Ligera Fiebre"
Send-ArduinoData -collar_id 5 -nombre_vaca "Venus" -mac_collar "AA:BB:CC:DD:EE:05" -temperatura 39.8 -pulsaciones 92 -escenario "Fiebre Moderada"
Send-ArduinoData -collar_id 1 -nombre_vaca "Marta" -mac_collar "AA:BB:CC:DD:EE:01" -temperatura 39.5 -pulsaciones 88 -escenario "Control Marta"

Write-Host "`n--- ESTADO CRITICO (>40C) ---" -ForegroundColor Red
Send-ArduinoData -collar_id 6 -nombre_vaca "Dalia" -mac_collar "AA:BB:CC:DD:EE:06" -temperatura 40.5 -pulsaciones 105 -escenario "Condicion Critica"
Send-ArduinoData -collar_id 7 -nombre_vaca "Iris" -mac_collar "AA:BB:CC:DD:EE:07" -temperatura 41.2 -pulsaciones 115 -escenario "Estado Critico Severo"
Send-ArduinoData -collar_id 2 -nombre_vaca "Rosa" -mac_collar "AA:BB:CC:DD:EE:02" -temperatura 40.8 -pulsaciones 110 -escenario "Control Rosa Critico"

Write-Host "`n==== 9 PRUEBAS COMPLETADAS ====" -ForegroundColor Cyan
Write-Host "Verifica en http://127.0.0.1:8000/admin para ver las lecturas"
