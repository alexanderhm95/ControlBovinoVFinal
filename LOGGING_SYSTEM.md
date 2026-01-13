# 📊 SISTEMA DE LOGGING - CONTROL BOVINO

## Descripción General

Se ha implementado un **sistema completo de logging** en el proyecto para registrar y monitorear:
- ✅ Solicitudes y respuestas de APIs
- ✅ Errores y excepciones
- ✅ Operaciones de base de datos
- ✅ Actividad de usuarios
- ✅ Datos del Arduino
- ✅ Accesos a vistas
- ✅ Intentos de login

---

## 📁 Estructura de Archivos de Log

Los logs se guardan automáticamente en la carpeta `logs/` del proyecto:

```
logs/
├── django.log          # Logs generales de Django
├── apis.log           # Logs específicos de APIs REST
├── errors.log         # Errores del sistema
├── database.log       # Operaciones de base de datos
├── requests.log       # Solicitudes HTTP
└── (se crean automáticamente)
```

### Tamaño Máximo de Logs
- **Máximo por archivo:** 10 MB
- **Backups automáticos:** 5 copias anteriores
- **Rotación automática:** Cuando se alcanza el límite

---

## 🔧 Configuración de Logging

La configuración está en `cardiaco_vaca/settings.py`:

### Niveles de Log
| Nivel | Descripción | Ejemplo |
|-------|-------------|---------|
| DEBUG | Información detallada | Detalles de ejecución |
| INFO | Información general | Accesos, operaciones exitosas |
| WARNING | Alertas importantes | Validaciones fallidas |
| ERROR | Errores | Excepciones, fallos |
| CRITICAL | Errores críticos | Sistema inutilizable |

### Formatos Disponibles

```
verbose:   [LEVEL] YYYY-MM-DD HH:MM:SS | logger_name | function:line | message
simple:    [LEVEL] HH:MM:SS | message
api_format: [API] YYYY-MM-DD HH:MM:SS | logger_name | LEVEL | message
```

---

## 📱 Módulo de Logging Personalizado

**Archivo:** `temp_car/logging_utils.py`

### Clases Disponibles

#### 1. APILogger
Registra solicitudes y respuestas de APIs

```python
from temp_car.logging_utils import APILogger

# Registrar solicitud
APILogger.log_request(
    endpoint='/api/movil/login/',
    method='POST',
    user=request.user,
    data={'username': 'admin@test.com'}
)

# Registrar respuesta
APILogger.log_response(
    endpoint='/api/movil/login/',
    status_code=200,
    method='POST',
    response_data={'message': 'Login exitoso'}
)

# Registrar error
APILogger.log_error(
    endpoint='/api/arduino/monitoreo',
    error='Datos incompletos',
    status_code=400
)
```

#### 2. ViewLogger
Registra accesos y errores en vistas

```python
from temp_car.logging_utils import ViewLogger

ViewLogger.log_view_access('monitoreo_actual', user=request.user)
ViewLogger.log_view_error('reportes', error)
```

#### 3. DatabaseLogger
Registra operaciones en base de datos

```python
from temp_car.logging_utils import DatabaseLogger

DatabaseLogger.log_query('Bovinos', 'CREATE')
DatabaseLogger.log_db_error('Lectura', 'Registro duplicado')
```

#### 4. MonitoringLogger
Registra alertas y eventos de monitoreo

```python
from temp_car.logging_utils import MonitoringLogger

MonitoringLogger.log_monitoring_alert(
    bovino_name='Sofia',
    collar_id=1,
    alert_type='temperatura_alta',
    value=40
)

MonitoringLogger.log_monitoring_success(
    bovino_name='Sofia',
    collar_id=1,
    temp=38.5,
    pulse=55
)
```

#### 5. ArduinoLogger
Registra datos del Arduino

```python
from temp_car.logging_utils import ArduinoLogger

ArduinoLogger.log_arduino_data(
    collar_id=1,
    bovino_name='Sofia',
    temp=38.5,
    pulse=55
)

ArduinoLogger.log_arduino_error('Error de conexión')
ArduinoLogger.log_arduino_validation_error(data, missing_fields)
```

#### 6. UserActivityLogger
Registra actividad de usuarios

```python
from temp_car.logging_utils import UserActivityLogger

UserActivityLogger.log_login(username='admin@test.com', success=True)
UserActivityLogger.log_logout(username='admin@test.com')
UserActivityLogger.log_user_action('admin@test.com', 'crear_usuario', 'newuser@test.com')
UserActivityLogger.log_registration('newuser@test.com', 'newuser@test.com')
```

---

## 🌐 Rutas de Visualización de Logs

Se han agregado nuevas rutas para administradores:

### 1. Dashboard de Logs
```
GET /admin/logs/
```
- Muestra resumen de todos los archivos de log
- Requiere ser staff (administrador)
- Respuesta: JSON con contenido de logs

**Ejemplo:**
```bash
curl -H "Cookie: sessionid=xxx" http://localhost:8000/admin/logs/
```

### 2. Obtener Contenido de Log Específico
```
GET /admin/logs/file/<filename>/?lines=50
```
- Muestra últimas N líneas de un archivo
- `filename`: `django.log`, `apis.log`, `errors.log`, etc.
- `lines`: número de líneas a mostrar (default: 50)

**Ejemplo:**
```bash
curl -H "Cookie: sessionid=xxx" http://localhost:8000/admin/logs/file/apis.log/?lines=100
```

### 3. Descargar Archivo de Log
```
GET /admin/logs/download/<filename>/
```
- Descarga el archivo completo
- Útil para análisis offline

### 4. Limpiar un Archivo de Log
```
DELETE /admin/logs/clear/<filename>/
```
- Borra el contenido del archivo
- Solo para administradores

### 5. Estadísticas de Logs
```
GET /admin/logs/stats/
```
- Muestra estadísticas de todos los logs:
  - Tamaño total
  - Conteo de eventos por tipo
  - Conteo de errores y advertencias

**Ejemplo de respuesta:**
```json
{
  "stats": {
    "total_log_files": 5,
    "total_size_kb": 250.5,
    "files": {
      "apis.log": {
        "size_kb": 100.2,
        "size_mb": 0.10,
        "stats": {
          "api_requests": 150,
          "api_responses": 145,
          "api_errors": 5,
          "errors": 8,
          "warnings": 12
        }
      },
      "errors.log": {
        "size_kb": 50.1,
        "stats": {
          "errors": 45,
          "warnings": 23
        }
      }
    }
  },
  "timestamp": "2026-01-12 20:10:00"
}
```

---

## 🎯 Ejemplos de Uso en APIs

### Ejemplo en `lecturaDatosArduino` (Arduino API)

```python
from temp_car.logging_utils import ArduinoLogger

@csrf_exempt
def lecturaDatosArduino(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        body_unicode = request.body.decode('utf-8')
        lecturaDecoded = json.loads(body_unicode)
        
        collar_id = lecturaDecoded.get('collar_id')
        nombre_vaca = lecturaDecoded.get('nombre_vaca')
        temperatura = lecturaDecoded.get('temperatura')
        pulsaciones = lecturaDecoded.get('pulsaciones', random.randint(41, 60))
        
        # Registrar datos recibidos
        ArduinoLogger.log_arduino_data(collar_id, nombre_vaca, temperatura, pulsaciones)
        
        # ... resto de la lógica ...
        
        return JsonResponse({'mensaje': 'Éxito'}, status=201)
        
    except json.JSONDecodeError:
        ArduinoLogger.log_arduino_error('JSON inválido en lectura')
        return JsonResponse({'error': 'JSON inválido'}, status=400)
```

### Ejemplo en `LoginView1` (Login API)

```python
from temp_car.logging_utils import APILogger, UserActivityLogger

class LoginView1(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        APILogger.log_request(
            '/api/movil/login/',
            'POST',
            data={'username': username}
        )
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            UserActivityLogger.log_login(username, success=True)
            login(request, user)
            
            APILogger.log_response(
                '/api/movil/login/',
                200,
                'POST',
                {'message': 'Login exitoso'}
            )
            return Response({'detalle': 'Inicio de sesión exitoso'}, status=200)
        else:
            UserActivityLogger.log_login(username, success=False)
            APILogger.log_error('/api/movil/login/', 'Credenciales inválidas', 401)
            return Response({'detalle': 'Credenciales inválidas'}, status=401)
```

---

## 📊 Monitoreo en Consola

Durante el desarrollo, los logs se muestran también en la **consola/terminal**:

```
[INFO] 2026-01-12 20:10:45 | temp_car | lecturaDatosArduino:750 | ARDUINO DATA | Collar: 1 | Bovino: Sofia | Temp: 38°C | Pulse: 55 bpm
[INFO] 2026-01-12 20:10:46 | temp_car | post:440 | API RESPONSE | POST /api/movil/login/ | Status: 200 | Data: {'message': 'Login exitoso'}
[ERROR] 2026-01-12 20:10:47 | temp_car | lecturaDatosArduino:800 | ARDUINO ERROR | Datos incompletos
```

---

## 🔍 Analizando Logs

### Ver logs en tiempo real
```bash
# En la terminal donde corre Django
# Los logs aparecen automáticamente

# O leer archivo específico
tail -f logs/apis.log
```

### Buscar eventos específicos
```bash
# Buscar errores de API
grep "API ERROR" logs/apis.log

# Buscar intentos de login fallidos
grep "LOGIN FAILED" logs/django.log

# Buscar datos del Arduino
grep "ARDUINO DATA" logs/apis.log
```

### Analizar estadísticas
```bash
# Contar solicitudes por endpoint
grep "API REQUEST" logs/apis.log | wc -l

# Ver endpoints más usados
grep "API REQUEST" logs/apis.log | cut -d'|' -f2 | sort | uniq -c | sort -rn
```

---

## ⚙️ Configuración Avanzada

### Cambiar nivel de logging

En `settings.py`:
```python
LOGGING = {
    'loggers': {
        'temp_car': {
            'level': 'DEBUG',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        },
    },
}
```

### Agregar nuevo logger personalizado

```python
# En logging_utils.py
class CustomLogger:
    @staticmethod
    def log_custom_event(event_type, details):
        custom_logger = logging.getLogger('temp_car.custom')
        custom_logger.info(f"CUSTOM EVENT | Type: {event_type} | Details: {details}")
```

### Filtrar logs por usuario

```python
# En cualquier vista/API
logger.info(f"Usuario {request.user.username} ejecutó acción")
```

---

## 🛡️ Seguridad y Privacidad

⚠️ **Importante:**
- Los logs pueden contener información sensible (emails, etc.)
- Solo administradores pueden ver los logs
- Los logs se rotan automáticamente para evitar almacenamiento infinito
- **En producción:** Considere enviar logs a un servicio externo (ELK, Datadog, CloudWatch)

---

## 📈 Métricas Útiles

Puedes usar `/admin/logs/stats/` para obtener:
- Total de solicitudes API
- Tasa de errores
- Operaciones de base de datos
- Intentos de login
- Alertas de monitoreo

---

## 🐛 Troubleshooting

### Los logs no se escriben
1. Verificar que exista la carpeta `logs/`
2. Verificar permisos de escritura en la carpeta
3. Verificar que `LOGGING` esté configurado en `settings.py`

### Los logs están muy grandes
1. La rotación automática está configurada a 10 MB
2. Se mantienen 5 backups por archivo
3. Usar `/admin/logs/clear/<filename>/` para limpiar

### No puedo ver los logs
1. Debe ser administrador (`is_staff=True`)
2. Acceder como usuario normal a `/admin/logs/` da error 403
3. Verificar que esté autenticado

---

## 📚 Referencias

- Django Logging: https://docs.djangoproject.com/en/4.2/topics/logging/
- Python Logging: https://docs.python.org/3/library/logging.html
- RotatingFileHandler: https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler

