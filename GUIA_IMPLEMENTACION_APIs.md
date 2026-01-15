# Guía de Implementación y Testing - APIs ControlBovinoVFinal

## 🚀 Instalación y Configuración

### Backend (Django/Vercel)

#### 1. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del Backend:

```bash
# API Configuration
API_BASE_URL=https://pmonitunl.vercel.app/api
ARDUINO_API_KEY=sk_arduino_controlbovino_2024
JWT_SECRET=your_secret_key_change_this
TOKEN_EXPIRY_MINUTES=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log

# Sensores - Rangos normales
TEMP_MIN_NORMAL=38
TEMP_MAX_NORMAL=39
HR_MIN_NORMAL=60
HR_MAX_NORMAL=80

# Seguridad
CORS_ALLOWED_ORIGINS=https://pmonitunl.vercel.app,http://localhost:3000
```

#### 2. Cargar Configuración en Django
En `Backend/cardiaco_vaca/settings.py`:

```python
from API_CONFIG import *

# Usar configuración
ARDUINO_API_KEY = ARDUINO_API_KEY
JWT_SECRET = JWT_SECRET
TOKEN_EXPIRY_MINUTES = TOKEN_EXPIRY_MINUTES
```

---

### App Flutter (monitor_vaca_app)

#### 1. URL ya está configurada ✅
El archivo `lib/services/api_service.dart` ya tiene:
```dart
static const String _baseUrl = 'https://pmonitunl.vercel.app/api';
```

#### 2. Usar el ApiService en tu app

```dart
import 'package:monitor_vaca/services/api_service.dart';

// Login
final user = await ApiService.login('usuario', 'contraseña');
if (user != null) {
  print("✅ Login exitoso: ${user.username}");
}

// Obtener datos de un collar
final data = await ApiService.fetchData(context, 1);

// Enviar datos de sensores
final success = await ApiService.sendSensorData(
  username: 'usuario',
  collarId: 1,
  temperature: 38,
  heartRate: 72,
);

// Obtener monitoreo actual
final monitoring = await ApiService.getMonitoreoActual(1);

// Validar conexión
final isOnline = await ApiService.validateConnection();

// Logout
ApiService.logout();
```

---

### Arduino/ESP32 (tic_vaca_Arduino)

#### 1. Configurar Arduino IDE

Librerías Requeridas:
```
- ArduinoJson (v6.x o superior)
- HTTPClient
- WiFiConnection (incluida en el proyecto)
```

Instalar vía Arduino IDE: Sketch → Include Library → Manage Libraries

#### 2. Configurar API Key

Editar `tic_vaca_Arduino/DataSender.cpp`:

```cpp
// Cambiar esto:
const char* API_KEY = "YOUR_API_KEY_HERE";

// Por esto:
const char* API_KEY = "sk_arduino_controlbovino_2024"; // O la clave real
```

#### 3. Cargar el código en el ESP32

```bash
# Opción 1: Usar Arduino IDE
# Abrir tic_vaca/tic_vaca.ino
# Tools → Board → ESP32
# Tools → Port → Seleccionar puerto COM
# Sketch → Upload

# Opción 2: Usar platformio
cd tic_vaca_Arduino
platformio run --target upload
```

#### 4. Monitorear Conexión

```bash
# Ver logs seriales del Arduino
# En Arduino IDE: Tools → Serial Monitor
# Configurar 9600 baud rate

# Deberías ver:
# WiFi conectado
# === ENVIANDO DATOS AL SERVIDOR ===
# ✅ Respuesta HTTP: 201
# ✅ Datos enviados correctamente
```

---

## 🧪 Testing de APIs

### 1. Test del Endpoint Arduino → Backend

**Herramienta**: cURL, Postman, o Thunder Client

**Endpoint**: 
```
POST https://pmonitunl.vercel.app/api/arduino/monitoreo
```

**Headers**:
```
Content-Type: application/json
Authorization: Bearer sk_arduino_controlbovino_2024
```

**Body (JSON)**:
```json
{
  "collar_id": 2,
  "nombre_vaca": "Salome",
  "mac_collar": "AA:BB:CC:DD:EE:FF",
  "temperatura": 38.5,
  "pulsaciones": 72
}
```

**Respuesta Esperada (201 Created)**:
```json
{
  "mensaje": "Datos guardados exitosamente",
  "data": {
    "lectura_id": 123,
    "bovino": "Salome",
    "collar_id": 2,
    "temperatura": 38.5,
    "pulsaciones": 72,
    "estado_salud": "Normal",
    "bovino_nuevo": false,
    "timestamp": "2026-01-15T10:30:45"
  }
}
```

**Script de Test (cURL)**:
```bash
curl -X POST \
  https://pmonitunl.vercel.app/api/arduino/monitoreo \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk_arduino_controlbovino_2024' \
  -d '{
    "collar_id": 2,
    "nombre_vaca": "Salome",
    "mac_collar": "AA:BB:CC:DD:EE:FF",
    "temperatura": 38.5,
    "pulsaciones": 72
  }'
```

### 2. Test del Endpoint Flutter → Backend

**Test de Login**:
```dart
final user = await ApiService.login('admin', 'admin123');
assert(user != null);
assert(user!.username == 'admin');
print("✅ Login exitoso");
```

**Test de Obtener Datos**:
```dart
final data = await ApiService.fetchData(context, 1);
assert(data != null);
assert(data!['collar_id'] == 1);
print("✅ Datos obtenidos");
```

**Test de Enviar Datos**:
```dart
final success = await ApiService.sendSensorData(
  username: 'admin',
  collarId: 1,
  temperature: 38,
  heartRate: 72,
);
assert(success == true);
print("✅ Datos enviados");
```

**Test de Validar Conexión**:
```dart
final isOnline = await ApiService.validateConnection();
assert(isOnline == true);
print("✅ Servidor disponible");
```

### 3. Test con Postman

Crear colección de Postman con:

**1. Login**
- Method: POST
- URL: `https://pmonitunl.vercel.app/api/movil/login/`
- Body: 
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**2. Get Collar Data**
- Method: GET
- URL: `https://pmonitunl.vercel.app/api/movil/datos/1/`
- Headers: `Authorization: Bearer {token_from_login}`

**3. Get Real-time Monitoring**
- Method: GET
- URL: `https://pmonitunl.vercel.app/api/monitor/datos/1/`
- Headers: `Authorization: Bearer {token_from_login}`

---

## 📊 Verificación de Endpoints

### Endpoints Disponibles

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/movil/login/` | Login de usuario | No |
| GET | `/api/movil/datos/<id>/` | Obtener datos históricos | Sí |
| POST | `/api/movil/datos/` | Enviar datos de sensores | Sí |
| GET | `/api/monitor/datos/<id>/` | Monitoreo actual | Sí |
| GET | `/api/ultimo/registro/<id>/` | Último registro | Sí |
| POST | `/api/arduino/monitoreo` | Recibir datos Arduino | Opcional |

### Test de Todos los Endpoints

```bash
#!/bin/bash

BASE_URL="https://pmonitunl.vercel.app"
API_KEY="sk_arduino_controlbovino_2024"

echo "🔐 1. Testing Login..."
curl -X POST $BASE_URL/api/movil/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

echo -e "\n📤 2. Testing Arduino Send..."
curl -X POST $BASE_URL/api/arduino/monitoreo \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "collar_id": 2,
    "nombre_vaca": "TestVaca",
    "mac_collar": "AA:BB:CC:DD:EE:FF",
    "temperatura": 38.5,
    "pulsaciones": 72
  }'

echo -e "\n✅ Testing completado"
```

---

## 🐛 Solución de Problemas

### Arduino no puede conectar al servidor

1. Verificar WiFi conectado:
   ```cpp
   if (WiFi.status() == WL_CONNECTED) {
     Serial.println("✅ WiFi conectado");
   } else {
     Serial.println("❌ WiFi no conectado");
   }
   ```

2. Verificar certificado SSL:
   - La URL debe ser HTTPS ✅ (configurada)
   - ESP32 debe tener certificados actualizados

3. Verificar API Key:
   - Debe coincidir en Arduino y Backend

### Flutter no puede conectar

1. Verificar URL:
   ```dart
   print(ApiService._baseUrl); // Debe ser https://pmonitunl.vercel.app/api
   ```

2. Verificar internet:
   ```dart
   final online = await ApiService.validateConnection();
   ```

3. Verificar token:
   ```dart
   print(ApiService.getAuthToken());
   ```

### Backend devuelve 401 (No autorizado)

1. Verificar token JWT si Flutter:
   - Token puede estar expirado
   - Hacer login nuevamente

2. Verificar API Key si Arduino:
   - Debe coincidir con `ARDUINO_API_KEY` en settings

### Backend devuelve 400 (Datos inválidos)

1. Verificar que JSON está bien formado:
   ```bash
   echo '{"collar_id":2}' | jq .  # Valida JSON
   ```

2. Verificar campos requeridos:
   - Arduino: collar_id, nombre_vaca, mac_collar, temperatura
   - Flutter: username, password (login)

---

## 📈 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# En Vercel
vercel logs

# En Backend local
tail -f logs/api.log | grep ARDUINO
tail -f logs/api.log | grep FLUTTER
```

### Estructura de Logs

```
[ARDUINO] Nueva petición recibida
[ARDUINO] Método: POST
[ARDUINO] Body recibido (raw): {...}
[ARDUINO] JSON parseado: {...}
[ARDUINO] Datos extraídos:
  - collar_id: 2
  - nombre_vaca: Salome
  - temperatura: 38.5
[ARDUINO] Bovino ENCONTRADO: Salome
[ARDUINO] ✅ Respuesta enviada
```

---

## 📚 Documentación Adicional

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Flutter HTTP Package](https://pub.dev/packages/http)
- [Arduino JSON Library](https://arduinojson.org/)
- [ESP32 HTTP Client](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/protocols/esp_http_client.html)

---

## ✅ Checklist de Deployement

- [ ] Variables de entorno configuradas en Backend
- [ ] API_CONFIG.py actualizado con claves reales
- [ ] Flutter URL configurada a Vercel
- [ ] Arduino API Key configurada correctamente
- [ ] Tests de conectividad pasados
- [ ] Logs verificados en tiempo real
- [ ] HTTPS certificado válido (Vercel automático)
- [ ] CORS configurado correctamente
- [ ] Documentación actualizada
- [ ] Equipo informado de cambios
