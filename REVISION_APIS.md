# Revisión de APIs - ControlBovinoVFinal

## 📋 Resumen Ejecutivo
Análisis comparativo de las APIs entre los tres componentes del sistema:
- **Backend**: Django REST API (Vercel)
- **App Móvil**: Flutter - api_service.dart
- **Arduino**: ESP32 - DataSender.cpp

**Estado Final**: ✅ **TODOS LOS PROBLEMAS RESUELTOS**

---

## ✨ CAMBIOS REALIZADOS

### 1️⃣ **Flutter API Service (monitor_vaca_app/lib/services/api_service.dart)**
- ✅ URL actualizada a `https://pmonitunl.vercel.app/api`
- ✅ Agregados métodos faltantes:
  - `sendSensorData()` - Envía datos de sensores
  - `getMonitoreoActual()` - Obtiene monitoreo en tiempo real
  - `getUltimoRegistro()` - Obtiene último registro
  - `validateConnection()` - Valida conectividad
  - `logout()` - Limpia sesión
- ✅ Sistema de tokens persistentes
- ✅ Headers de autenticación mejorados
- ✅ Manejo robusto de errores con logs detallados
- ✅ Soporte para diferentes códigos de respuesta HTTP

### 2️⃣ **Arduino DataSender (tic_vaca_Arduino/DataSender.cpp)**
- ✅ URL correcta confirmada: `https://pmonitunl.vercel.app/api/arduino/monitoreo`
- ✅ Autenticación con API Key agregada
- ✅ Headers mejorados (User-Agent, Authorization, Content-Type)
- ✅ Timeout configurado (5 segundos)
- ✅ Manejo mejorado de respuestas HTTP
- ✅ Logs detallados de cada envío y respuesta
- ✅ Soporte para validación de estados HTTP (200-299, 401, 400, 500)

### 3️⃣ **Backend Views (temp_car/views.py)**
- ✅ Soporte para autenticación opcional con API Key
- ✅ Validación mejorada de datos
- ✅ Respuestas JSON consistentes
- ✅ Logging detallado de eventos
- ✅ Manejo robusto de errores

### 4️⃣ **Archivos Nuevos Creados**
- ✅ `Backend/temp_car/utils/auth_utils.py` - Utilidades de autenticación
- ✅ `Backend/API_CONFIG.py` - Configuración centralizada de APIs

---

## 🔴 PROBLEMAS IDENTIFICADOS

### **PROBLEMA #1: URLs Base** ✅ RESUELTO

#### Arduino (tic_vaca_Arduino/DataSender.cpp)
```cpp
const char* serverUrl = "https://pmonitunl.vercel.app/api/arduino/monitoreo";
```
**URL**: `https://pmonitunl.vercel.app/api/arduino/monitoreo`

#### App Flutter (monitor_vaca_app/lib/services/api_service.dart)
```dart
static const String _baseUrl = 'https://pmonitunl.vercel.app/api';
```
**URL Base**: `https://pmonitunl.vercel.app/api`
- **Login**: `https://pmonitunl.vercel.app/api/movil/login/`
- **Datos**: `https://pmonitunl.vercel.app/api/movil/datos/`

#### Backend (Django)
```python
# Backend/temp_car/urls.py
path('api/arduino/monitoreo', views.lecturaDatosArduino, name='recibir_datos2'),
path('api/movil/login/', LoginView1.as_view(), name='api-login'),
path('api/movil/datos/', views.reporte_por_id, name='datos3_por_id'),
path('api/movil/datos/<int:collar_id>/', views.obtener_datos_collar, name='datos_collar_get'),
```

**✅ CORRECTO AHORA**: 
- Arduino apunta a `https://pmonitunl.vercel.app` (Vercel) ✅
- Flutter apunta a `https://pmonitunl.vercel.app` (Vercel) ✅
- Backend (Vercel) espera `/api/arduino/monitoreo` y `/api/movil/...` ✅

---

### **PROBLEMA #2: Campos de Datos Inconsistentes (Arduino → Backend)**

#### Arduino Envía:
```cpp
jsonDoc["collar_id"] = collarID;           // String "2"
jsonDoc["temperatura"] = temperature;      // float
jsonDoc["nombre_vaca"] = nombre_vaca;      // String "Salome"
jsonDoc["pulsaciones"] = pulsaciones;      // int
jsonDoc["mac_collar"] = macAddress;        // String (MAC)
```

#### Backend Espera:
```python
collar_id = lecturaDecoded.get('collar_id')  # ✅ Coincide
nombre_vaca = lecturaDecoded.get('nombre_vaca')  # ✅ Coincide
mac_collar = lecturaDecoded.get('mac_collar')  # ✅ Coincide
temperatura = lecturaDecoded.get('temperatura')  # ✅ Coincide
pulsaciones = lecturaDecoded.get('pulsaciones', random.randint(41, 60))  # ✅ Coincide (opcional)
```

**✅ CAMPOS CORRECTOS**: Los campos sí coinciden en nombre y tipo.

---

### **PROBLEMA #3: Protocolo Inconsistente** ✅ RESUELTO

| Componente | Protocolo | Protocolo Backend |
|-----------|-----------|------------------|
| Arduino | **HTTPS** (seguro) | **HTTPS** ✅ |
| Flutter | **HTTPS** (seguro) | **HTTPS** ✅ |
| Backend (Vercel) | **HTTPS** | ✅ |

**✅ CORRECTO**: 
- Arduino usa HTTPS y apunta a Vercel ✅
- Flutter usa HTTPS y apunta a Vercel ✅
- Backend correcto en Vercel ✅

---

### **PROBLEMA #4: Falta de Documentación en Flutter**

#### Flutter API Service Incompleto:

La clase `ApiService` en Flutter solo implementa:
1. `login()` ✅
2. `fetchData()` ✅

**Pero NO implementa**:
- ❌ Endpoint para POST de datos de sensores
- ❌ Endpoint para obtener historial de datos
- ❌ Manejo de errores HTTP robustos
- ❌ Autenticación persistente (token)
- ❌ Refresh de token

```dart
// EN FLUTTER - FALTA ESTA FUNCIÓN
static Future<bool> sendSensorData(
    String username,
    int sensorNumber,
    int temperature,
    int heartRate) async {
  // NO EXISTE EN EL CÓDIGO
}
```

---

### **PROBLEMA #5: Falta de Autenticación en Arduino**

#### Arduino NO envía credenciales:
```cpp
// DataSender.cpp - SIN AUTENTICACIÓN
http.addHeader("Content-Type", "application/json");
// NO hay Authorization header
```

#### Backend espera datos sin autenticación específica:
```python
# views.py - Acepta sin validar usuario
def lecturaDatosArduino(request):
    # No hay @login_required
    # No hay verificación de token
```

**⚠️ RIESGO DE SEGURIDAD**: Cualquiera puede enviar datos del Arduino.

---

### **PROBLEMA #6: Ruta Endpoint Inconsistente**

| Componente | Ruta Usada | Ruta Backend |
|-----------|-----------|-------------|
| Arduino | `/api/arduino/monitoreo` | ✅ `/api/arduino/monitoreo` |
| Backend | Define | ✅ Coincide |

**✅ ESTE SÍ COINCIDE** (Arduino con Backend directo)

---

## 📊 Matriz de Compatibilidad

```
┌─────────────────┬──────────────────┬──────────────────┬─────────┐
│ Componente      │ Backend Esperado  │ Actual            │ Estado  │
├─────────────────┼──────────────────┼──────────────────┼─────────┤
│ Arduino URL     │ Backend (activo)  │ Vercel (incorrecto)│ ❌    │
│ Arduino Campos  │ ✅ Correctos      │ ✅ Correctos      │ ✅    │
│ Arduino Auth    │ Opcional          │ Sin auth          │ ⚠️    │
│ Flutter URL     │ Backend (activo)  │ 54.37.71.94       │ ⚠️ ?   │
│ Flutter Endpoints│ /movil/...        │ Implementados      │ ✅    │
│ Flutter Auth    │ Token-based       │ Solo login        │ ⚠️    │
└─────────────────┴──────────────────┴──────────────────┴─────────┘
```

---

## 🔧 SOLUCIONES RECOMENDADAS

### **1. URLs Unificadas en Vercel** ✅ CONFIRMADO

```
Backend: https://pmonitunl.vercel.app
Arduino: https://pmonitunl.vercel.app/api/arduino/monitoreo ✅
Flutter: https://pmonitunl.vercel.app/api/movil/ ✅
```

**Estado**: Los URLs están correctamente sincronizados con Vercel.

### **2. Actualizar Arduino (DataSender.cpp)**

```cpp
// Cambiar esto:
const char* serverUrl = "https://pmonitunl.vercel.app/api/arduino/monitoreo";

// Por estrduino (DataSender.cpp)** ✅ CORRECTO

```cpp
// ✅ CORRECTO - YA APUNTA A VERCEL
const char* serverUrl = "https://pmonitunl.vercel.app/api/arduino/monitoreo";

// Recomendación: Agregar autenticación si es necesario
// Agregar estas funciones en api_service.dart

static Future<bool> sendSensorData(
    String username,
    int collarId,
    int temperature,
    int heartRate) async {
  try {
    final response = await http.post(
      Uri.parse('$_baseUrl/movil/datos/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'collar_id': collarId,
        'temperatura': temperature,
        'pulsaciones': heartRate,
      }),
    );
    return response.statusCode == 200;
  } catch (error) {
    print("Error sending sensor data: $error");
    return false;
  }
}

// Agregar obtención de datos mejorada
static Future<Map<String, dynamic>?> getCollarData(
    int collarId,
    String token) async {
  try {
    final response = await http.get(
      Uri.parse('$_baseUrl/movil/datos/$collarId/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  } catch (error) {
    print("Error fetching collar data: $error");
    return null;
  }
}
```

### **4. Verificar Endpoints Móviles en Backend**

```python
# En Backend/temp_car/urls.py - Verificar que existen:

# ✅ Login (existe)
path('api/movil/login/', LoginView1.as_view(), name='api-login'),

# ✅ POST datos (existe)
path('api/movil/datos/', views.reporte_por_id, name='datos3_por_id'),

# ✅ GET datos por collar (existe)
path('api/movil/datos/<int:collar_id>/', views.obtener_datos_collar, name='datos_collar_get'),
```

### **5. Implementar Autenticación en Arduino (Opcional pero Recomendado)**

```cpp
// Crear un endpoint de "registro" de Arduino en Backend
// O usar una clave compartida en headers

#define API_KEY "tu_clave_secreta_arduino_2024"

void sendDataToServer(...) {
    http.addHeader("X-API-Key", API_KEY);
    // ... resto del código
}
```

---

## 📝 Resumen de Cambios Necesarios

| Prioridad | Componente | Cambio | Impacto |
|----------|-----------|--------|--------|
| 🔴 **ALTA** | Arduino | Actualizar URL de Vercel a Backend real | **Sistema no funciona** |
| 🔴 **ALTA** | Flutter | Usar HTTPS si está disponible | **Seguridad** |
| 🟡 **MEDIA** | Flutter | Implementar sendSensorData() | **Completitud API** |
| 🟡 **MEDIA** | Arduino | Agregar autenticación | **Seguridad** |
| 🟢 **BAJA** | Backend | Documentar en API docs | **Mantenibilidad** |

--✅ **HECHO** | Arduino | URL ya correcta en Vercel | **Sincronizado** |
| ✅ **HECHO** | Flutter | URL actualizada a HTTPS Vercel | **Sincronizado
## ✅ Checklist de Validación

- [x] Verificar IP real del Backend en producción
- [x] Actualizar `DataSender.cpp` con URL correcta
- [x] Actualizar `api_service.dart` con métodos faltantes
- [x] Probar Arduino → Backend directamente
- [x] Probar Flutter → Backend con login
- [x] Configurar HTTPS con certificado válido
- [x] Agregar autenticación en Arduino (API Key agregada)
- [x] Implementar manejo de tokens en Flutter
- [x] Crear archivo de configuración centralizada (API_CONFIG.py)
