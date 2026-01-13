# ⚡ GUÍA RÁPIDA - CONTROL BOVINO

## 🚀 Iniciar el Proyecto

```bash
# 1. Activar entorno virtual
.\.venv\Scripts\activate

# 2. Iniciar servidor Django
python manage.py runserver

# 3. En otra terminal - Ejecutar pruebas
python test_final.py
```

---

## 📱 APIs Principales

### Login (Mobile)
```bash
POST /api/movil/login/
Body: {"username": "admin@test.com", "password": "admin123"}
Response: {"detalle": "Inicio de sesión exitoso", "data": {...}}
```

### Dashboard Data
```bash
GET /monitor/datos/1/
Response: {"collar_info": {...}, "ultimos_registros": [...]}
```

### Registrar Monitoreo
```bash
POST /api/movil/datos/
Body: {sensor: "1", username: "admin@test.com"}
Response: {"reporte": {...}}
```

### Datos Arduino
```bash
POST /api/arduino/monitoreo
Body: {
  "collar_id": 1,
  "nombre_vaca": "Sofia",
  "mac_collar": "AA:BB:CC:DD:EE:FF",
  "temperatura": 38,
  "pulsaciones": 55
}
Response: {"mensaje": "Éxito", "data": {...}}
```

### Gestión de Usuarios
```bash
# Registrar
POST /api/register
Body: {cedula, telefono, nombre, apellido, email}

# Listar
GET /api/listar
Response: {"usuarios": {...}, "total": N}

# Editar
POST /api/editar/<user_id>/
Body: {cedula, telefono, nombre, apellido, email}
```

---

## 📊 Logs y Monitoreo

### Ver Logs (Admin Only)
```bash
GET /admin/logs/                          # Dashboard
GET /admin/logs/file/apis.log/?lines=50   # Ver archivo
GET /admin/logs/stats/                    # Estadísticas
DELETE /admin/logs/clear/apis.log/        # Limpiar
```

### Usar Logging en Código
```python
from temp_car.logging_utils import APILogger, ArduinoLogger

APILogger.log_request(endpoint, method, user=request.user)
APILogger.log_response(endpoint, status_code)
APILogger.log_error(endpoint, error)

ArduinoLogger.log_arduino_data(collar_id, bovino_name, temp, pulse)
```

---

## 🧪 Testing

```bash
# Test completo de todas las APIs
python test_final.py

# Output esperado: 9-10/10 ✓ PASS
```

---

## 🔑 Credenciales de Prueba

```
Usuario: admin@test.com
Password: admin123

Usuario: test@test.com
Password: test123
```

---

## 📁 Estructura de Carpetas

```
ControlBovinoVFinal/
├── temp_car/
│   ├── views.py              # APIs principales
│   ├── models.py             # Modelos de BD
│   ├── logging_utils.py      # 🆕 Logging personalizado
│   ├── logs_views.py         # 🆕 Vistas de logs
│   ├── urls.py               # Rutas
│   └── templates/            # Templates HTML
├── cardiaco_vaca/
│   ├── settings.py           # Configuración + logging
│   ├── urls.py               # URLs principales
│   └── wsgi.py
├── logs/                      # 🆕 Carpeta de logs
│   ├── django.log
│   ├── apis.log
│   ├── errors.log
│   └── ...
├── APIS_COMPLETAS.md         # 📖 Documentación de APIs
├── LOGGING_SYSTEM.md         # 📖 Documentación de logs
├── RESUMEN_FINAL.md          # 📖 Resumen del proyecto
└── manage.py
```

---

## 🔧 Troubleshooting

### Servidor no inicia
```
Error: ModuleNotFoundError: No module named 'dj_database_url'
Solución: pip install dj-database-url psycopg2-binary
```

### Carpeta logs no existe
```
Error: [Errno 2] No such file or directory: 'logs'
Solución: Se crea automáticamente, o crear manualmente: mkdir logs
```

### No puedo ver los logs
```
Error: Acceso denegado al /admin/logs/
Solución: Debes ser administrador. Usa: python manage.py createsuperuser
```

---

## 📊 Comandos Útiles

```bash
# Crear superusuario
python manage.py createsuperuser

# Migraciones
python manage.py migrate
python manage.py makemigrations

# Shell Django
python manage.py shell

# Crear datos de prueba
python setup_test_data.py

# Ver logs en tiempo real
tail -f logs/apis.log
```

---

## 🎯 Endpoints Rápidos

| Categoría | Endpoint | Método | Status |
|-----------|----------|--------|--------|
| Dashboard | `/monitor/datos/1/` | GET | ✅ |
| Dashboard | `/ultimo/registro/1` | GET | ✅ |
| Mobile | `/api/movil/login/` | POST | ✅ |
| Mobile | `/api/movil/datos/` | POST | ✅ |
| Users | `/api/register` | POST | ✅ |
| Users | `/api/listar` | GET | ✅ |
| Users | `/api/editar/<id>/` | POST | ✅ |
| Arduino | `/api/arduino/monitoreo` | POST | ✅ |
| Logs | `/admin/logs/` | GET | ✅ |
| Logs | `/admin/logs/stats/` | GET | ✅ |

---

## 📚 Documentación Completa

- **APIs**: [APIS_COMPLETAS.md](APIS_COMPLETAS.md) - 25 endpoints documentados
- **Logging**: [LOGGING_SYSTEM.md](LOGGING_SYSTEM.md) - Sistema de logs completo
- **Resumen**: [RESUMEN_FINAL.md](RESUMEN_FINAL.md) - Resumen del proyecto

---

## 💡 Tips

1. **Ver logs mientras se ejecuta**
   ```bash
   # Terminal 1
   python manage.py runserver
   
   # Terminal 2
   tail -f logs/apis.log
   ```

2. **Buscar en logs**
   ```bash
   grep "ERROR" logs/apis.log
   grep "Arduino" logs/apis.log
   grep "LOGIN" logs/django.log
   ```

3. **Estadísticas rápidas**
   - Acceder a: `http://localhost:8000/admin/logs/stats/`
   - Ver JSON con conteo de eventos

4. **Exportar logs**
   - Descargar desde: `/admin/logs/download/apis.log/`
   - O copiar desde: `logs/apis.log`

---

## ✅ Checklist de Desarrollo

- [ ] Clonar proyecto
- [ ] Crear entorno virtual: `python -m venv .venv`
- [ ] Activar: `.\.venv\Scripts\activate`
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Iniciar servidor: `python manage.py runserver`
- [ ] Ejecutar tests: `python test_final.py`
- [ ] Ver logs: `curl http://localhost:8000/admin/logs/`
- [ ] Crear superusuario: `python manage.py createsuperuser`
- [ ] ¡A desarrollar! 🚀

---

**Última actualización:** 12 de Enero de 2026
**Versión:** 1.0
**Estado:** ✅ Producción

