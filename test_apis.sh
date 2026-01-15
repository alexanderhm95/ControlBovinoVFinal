#!/bin/bash

# QUICK START - Control Bovino APIs
# Ejecutar estos comandos para verificar que todo funciona

echo "🔍 TESTING APIs - ControlBovinoVFinal"
echo "======================================"
echo ""

# Variable base
BASE_URL="https://pmonitunl.vercel.app"
API_KEY="sk_arduino_controlbovino_2024"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

echo "1️⃣ TEST DE CONECTIVIDAD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

curl -s -I $BASE_URL > /dev/null
print_status $? "Servidor Vercel disponible"

echo ""
echo "2️⃣ TEST DE LOGIN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Intentando login con admin/admin123..."

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/movil/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }')

echo "Respuesta:"
echo "$LOGIN_RESPONSE" | head -c 200
echo "..."
echo ""

# Extraer token (si existe)
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4 || echo "")

if [ ! -z "$TOKEN" ]; then
    echo -e "${GREEN}✅ Login exitoso - Token obtenido${NC}"
else
    echo -e "${YELLOW}⚠️  Token no obtenido (puede ser normal si no usa JWT)${NC}"
fi

echo ""
echo "3️⃣ TEST DE ARDUINO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Enviando datos de prueba al endpoint de Arduino..."

ARDUINO_RESPONSE=$(curl -s -X POST "$BASE_URL/api/arduino/monitoreo" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "collar_id": 2,
    "nombre_vaca": "TestVaca",
    "mac_collar": "AA:BB:CC:DD:EE:FF",
    "temperatura": 38.5,
    "pulsaciones": 72
  }')

echo "Respuesta:"
echo "$ARDUINO_RESPONSE" | jq . 2>/dev/null || echo "$ARDUINO_RESPONSE"
echo ""

echo "4️⃣ TEST DE ENDPOINTS MÓVILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

AUTH_HEADER="Authorization: Bearer $TOKEN"

echo "4a) GET /api/movil/datos/1/..."
curl -s -X GET "$BASE_URL/api/movil/datos/1/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" | jq . 2>/dev/null | head -c 200
echo ""
echo ""

echo "4b) GET /api/monitor/datos/1/..."
curl -s -X GET "$BASE_URL/api/monitor/datos/1/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" | jq . 2>/dev/null | head -c 200
echo ""
echo ""

echo "4c) GET /api/ultimo/registro/1..."
curl -s -X GET "$BASE_URL/api/ultimo/registro/1" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" | jq . 2>/dev/null | head -c 200
echo ""
echo ""

echo "════════════════════════════════════════════════════════════"
echo "📊 RESUMEN DE TESTS"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ Endpoints disponibles:"
echo "   • POST /api/movil/login/"
echo "   • GET  /api/movil/datos/<id>/"
echo "   • POST /api/movil/datos/"
echo "   • GET  /api/monitor/datos/<id>/"
echo "   • GET  /api/ultimo/registro/<id>"
echo "   • POST /api/arduino/monitoreo"
echo ""
echo "🔗 Base URL: $BASE_URL"
echo "🔐 API Key: ${API_KEY:0:20}..."
echo ""
echo "📚 Para más información, ver:"
echo "   • GUIA_IMPLEMENTACION_APIs.md"
echo "   • REVISION_APIS.md"
echo "   • RESUMEN_CAMBIOS_APIS.md"
echo ""
echo "════════════════════════════════════════════════════════════"

# Script en Windows PowerShell (PS1)
cat > test_apis.ps1 << 'EOF'
# QUICK START - Control Bovino APIs (PowerShell)
# Ejecutar: powershell -ExecutionPolicy Bypass -File test_apis.ps1

$BASE_URL = "https://pmonitunl.vercel.app"
$API_KEY = "sk_arduino_controlbovino_2024"

Write-Host "🔍 TESTING APIs - ControlBovinoVFinal" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 1. Test conectividad
Write-Host "1️⃣ TEST DE CONECTIVIDAD" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

try {
    $response = Invoke-WebRequest -Uri $BASE_URL -Method Head -TimeoutSec 5 -SkipHttpErrorCheck
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Servidor disponible" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Servidor responde con código: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error de conectividad: $_" -ForegroundColor Red
}

Write-Host ""

# 2. Test Login
Write-Host "2️⃣ TEST DE LOGIN" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

try {
    $loginBody = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/api/movil/login/" `
                                 -Method Post `
                                 -Headers @{"Content-Type" = "application/json"} `
                                 -Body $loginBody `
                                 -SkipHttpErrorCheck

    Write-Host "Respuesta:"
    Write-Host ($response | ConvertTo-Json | Select-Object -First 3) -ForegroundColor Green
    
    if ($response.token) {
        Write-Host "✅ Login exitoso - Token obtenido" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Error en login: $_" -ForegroundColor Yellow
}

Write-Host ""

# 3. Test Arduino
Write-Host "3️⃣ TEST DE ARDUINO" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

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

    Write-Host "✅ Datos enviados correctamente" -ForegroundColor Green
    Write-Host "Respuesta:"
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "❌ Error en Arduino: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Testing completado" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
EOF

echo ""
echo "📁 Script guardado como: test_apis.ps1"
echo "   Ejecutar en PowerShell con:"
echo "   powershell -ExecutionPolicy Bypass -File test_apis.ps1"
