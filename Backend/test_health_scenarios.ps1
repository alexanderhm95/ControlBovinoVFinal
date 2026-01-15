# Script para probar múltiples escenarios de salud de las vacas
# Escenarios: Normal, Alert, Critical

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
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "Escenario: $escenario" -ForegroundColor Yellow
    Write-Host "Collar: $nombre_vaca (ID: $collar_id)" -ForegroundColor Green
    Write-Host "Temperatura: ${temperatura}°C | Pulsaciones: $pulsaciones BPM" -ForegroundColor Magenta
    
    try {
        $response = Invoke-RestMethod -Uri $baseUrl -Method POST -Headers $headers -Body $body -ErrorAction Stop
        
        $statusColor = switch ($response.estado_salud) {
            "Normal" { "Green" }
            "Alerta" { "Yellow" }
            "Crítico" { "Red" }
            default { "White" }
        }
        
        Write-Host "Estado de Salud: $($response.estado_salud)" -ForegroundColor $statusColor
        Write-Host "ID Lectura: $($response.id)" -ForegroundColor Cyan
        Write-Host "Respuesta: 201 Created ✓" -ForegroundColor Green
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}


# ============================================================
# PRUEBAS: 3 ESCENARIOS DE SALUD
# ============================================================

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  PRUEBAS DE SALUD - MÚLTIPLES ESCENARIOS                ║" -ForegroundColor Cyan
Write-Host "║  Normal: 36-39°C | Alerta: 39-40°C | Crítico: >40°C   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ESCENARIO 1: NORMAL (36-39°C)
Write-Host "`n→ ESCENARIO 1: ESTADO NORMAL (36-39°C)" -ForegroundColor Green
Send-ArduinoData -collar_id 1 -nombre_vaca "Marta" -mac_collar "AA:BB:CC:DD:EE:01" -temperatura 37.2 -pulsaciones 65 -escenario "Vaca Sana - Temperatura Normal"
Send-ArduinoData -collar_id 2 -nombre_vaca "Rosa" -mac_collar "AA:BB:CC:DD:EE:02" -temperatura 38.1 -pulsaciones 72 -escenario "Vaca Sana - Temperatura Óptima"
Send-ArduinoData -collar_id 3 -nombre_vaca "Bella" -mac_collar "AA:BB:CC:DD:EE:03" -temperatura 36.5 -pulsaciones 58 -escenario "Vaca Sana - Temperatura Baja Normal"

# ESCENARIO 2: ALERTA (39-40°C)
Write-Host "`n→ ESCENARIO 2: ESTADO ALERTA (39-40°C)" -ForegroundColor Yellow
Send-ArduinoData -collar_id 4 -nombre_vaca "Paloma" -mac_collar "AA:BB:CC:DD:EE:04" -temperatura 39.2 -pulsaciones 85 -escenario "Vaca con Ligera Fiebre"
Send-ArduinoData -collar_id 5 -nombre_vaca "Venus" -mac_collar "AA:BB:CC:DD:EE:05" -temperatura 39.8 -pulsaciones 92 -escenario "Vaca con Fiebre Moderada"
Send-ArduinoData -collar_id 1 -nombre_vaca "Marta" -mac_collar "AA:BB:CC:DD:EE:01" -temperatura 39.5 -pulsaciones 88 -escenario "Alerta - Control Marta"

# ESCENARIO 3: CRÍTICO (>40°C)
Write-Host "`n→ ESCENARIO 3: ESTADO CRÍTICO (>40°C)" -ForegroundColor Red
Send-ArduinoData -collar_id 6 -nombre_vaca "Dalia" -mac_collar "AA:BB:CC:DD:EE:06" -temperatura 40.5 -pulsaciones 105 -escenario "Vaca en Condición Crítica"
Send-ArduinoData -collar_id 7 -nombre_vaca "Iris" -mac_collar "AA:BB:CC:DD:EE:07" -temperatura 41.2 -pulsaciones 115 -escenario "Vaca en Estado Crítico Severo"
Send-ArduinoData -collar_id 2 -nombre_vaca "Rosa" -mac_collar "AA:BB:CC:DD:EE:02" -temperatura 40.8 -pulsaciones 110 -escenario "Crítico - Control Rosa"

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  PRUEBAS COMPLETADAS                                   ║" -ForegroundColor Cyan
Write-Host "║  Total: 9 lecturas enviadas                            ║" -ForegroundColor Cyan
Write-Host "║  • 3 Estado Normal                                      ║" -ForegroundColor Green
Write-Host "║  • 3 Estado Alerta                                      ║" -ForegroundColor Yellow
Write-Host "║  • 3 Estado Crítico                                     ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Verifica en el Backend (http://127.0.0.1:8000/admin) para ver todas las lecturas."
