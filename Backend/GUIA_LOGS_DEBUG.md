# 📊 GUÍA DE MONITOREO DE LOGS EN TIEMPO REAL

## 🎯 Sistema de Debug Implementado

Se han agregado prints detallados en las APIs de:
- **Arduino/ESP32** (`/api/arduino/monitoreo`)
- **Móvil** (`/api/movil/datos/`)

## 📝 ¿Qué se registra?

### Para Arduino:
- ✅ Método HTTP y headers recibidos
- ✅ Body raw y JSON parseado
- ✅ Datos extraídos (collar_id, nombre, temperatura, pulsaciones, etc.)
- ✅ Operaciones en base de datos (crear/actualizar bovino)
- ✅ IDs generados (temperatura, pulsaciones, lectura)
- ✅ Estado de salud calculado
- ✅ Respuesta enviada
- ❌ Errores con traceback completo

### Para Móvil:
- ✅ Método HTTP y headers
- ✅ Body y JSON parseado
- ✅ Parámetros (collar_id, username)
- ✅ Búsqueda de bovino y usuario
- ✅ Verificación de condiciones (mañana/tarde)
- ✅ Registro de control de monitoreo
- ✅ Respuesta completa con reporte
- ❌ Errores con traceback

## 🚀 Cómo Ver los Logs

### Opción 1: Ver TODOS los logs en tiempo real

```bash
./ver_logs_directo.sh
```

o manualmente:

```bash
sudo journalctl -u gunicorn-controlbovino -f --no-pager
```

### Opción 2: Ver logs FILTRADOS

```bash
./ver_logs_filtrados.sh
```

Opciones del menú:
1. Ver solo logs de **ARDUINO**
2. Ver solo logs de **MÓVIL**
3. Ver todos los logs con debug
4. Ver logs de **ERRORES** solamente
5. Ver últimas 50 líneas de todos los logs

### Opción 3: Comandos manuales

Ver solo Arduino:
```bash
sudo journalctl -u gunicorn-controlbovino -f | grep "\[ARDUINO\]"
```

Ver solo Móvil:
```bash
sudo journalctl -u gunicorn-controlbovino -f | grep "\[MÓVIL\]"
```

Ver solo errores:
```bash
sudo journalctl -u gunicorn-controlbovino -f | grep -E "ERROR|❌"
```

Ver últimas 100 líneas:
```bash
sudo journalctl -u gunicorn-controlbovino -n 100 --no-pager
```

## 📋 Ejemplo de Salida

### Petición de Arduino:
```
================================================================================
[ARDUINO] Nueva petición recibida
[ARDUINO] Método: POST
[ARDUINO] Headers: {'Content-Type': 'application/json', ...}
[ARDUINO] Content-Type: application/json
================================================================================
[ARDUINO] Body recibido (raw): {"collar_id": 1, "nombre_vaca": "Sofia", ...}
[ARDUINO] JSON parseado: {'collar_id': 1, 'nombre_vaca': 'Sofia', ...}
[ARDUINO] Datos extraídos:
  - collar_id: 1
  - nombre_vaca: Sofia
  - mac_collar: AA:BB:CC:DD:EE:FF
  - temperatura: 38
  - pulsaciones: 55
[ARDUINO] Buscando/creando bovino con collar_id=1...
[ARDUINO] Bovino ENCONTRADO: Sofia (ID: 4)
[ARDUINO] Actualizando nombre: Test Debug -> Sofia
[ARDUINO] Creando registros de sensores...
[ARDUINO] Temperatura ID: 105, Pulsaciones ID: 105
[ARDUINO] Lectura creada ID: 105
[ARDUINO] Estado de salud: Alerta
[ARDUINO] ✅ Respuesta enviada: {'mensaje': 'Datos guardados exitosamente', ...}
================================================================================
```

### Petición de Móvil:
```
================================================================================
[MÓVIL] Nueva petición de reporte recibida
[MÓVIL] Método: POST
[MÓVIL] Headers: {...}
================================================================================
[MÓVIL] Body recibido: {"sensor": "1", "username": "user@example.com"}
[MÓVIL] JSON parseado: {'sensor': '1', 'username': 'user@example.com'}
[MÓVIL] Parámetros extraídos:
  - collar_id: 1
  - username: user@example.com
[MÓVIL] Buscando bovino con collar_id=1...
[MÓVIL] ✓ Bovino encontrado: Sofia
[MÓVIL] Buscando usuario: user@example.com...
[MÓVIL] ✓ Usuario encontrado: user@example.com
[MÓVIL] Verificando condiciones de registro...
[MÓVIL]   - Última lectura: 2026-01-14 22:28:32
[MÓVIL]   - Estado de salud: Alerta
[MÓVIL] ✓ Condiciones cumplidas para turno MAÑANA
[MÓVIL] ✅ Respuesta enviada: {'collar_id': 1, 'nombre_vaca': 'Sofia', ...}
================================================================================
```

## 🛠️ Probar el Sistema

### Probar API de Arduino:
```bash
curl -X POST http://190.96.102.30:8081/api/arduino/monitoreo \
  -H "Content-Type: application/json" \
  -d '{
    "collar_id": 1,
    "nombre_vaca": "Test Debug",
    "mac_collar": "AA:BB:CC:DD:EE:FF",
    "temperatura": 38,
    "pulsaciones": 55
  }'
```

### Probar API de Móvil:
```bash
curl -X POST http://190.96.102.30:8081/api/movil/datos/ \
  -H "Content-Type: application/json" \
  -d '{
    "sensor": "1",
    "username": "baherreram@gmail.com"
  }'
```

## 📊 Archivos de Log

Además de los prints en tiempo real, el sistema guarda logs en:

- **Django general**: `/home/administrador/ControlBovinoVFinal/logs/django.log`
- **Requests**: `/home/administrador/ControlBovinoVFinal/logs/requests.log`
- **Errores**: `/home/administrador/ControlBovinoVFinal/logs/errors.log`
- **Base de datos**: `/home/administrador/ControlBovinoVFinal/logs/database.log`

Ver archivos de log:
```bash
tail -f /home/administrador/ControlBovinoVFinal/logs/requests.log
tail -f /home/administrador/ControlBovinoVFinal/logs/errors.log
```

## ⚙️ Control del Servicio

Reiniciar gunicorn (aplicar cambios):
```bash
sudo systemctl restart gunicorn-controlbovino
```

Ver estado:
```bash
sudo systemctl status gunicorn-controlbovino
```

Detener:
```bash
sudo systemctl stop gunicorn-controlbovino
```

Iniciar:
```bash
sudo systemctl start gunicorn-controlbovino
```

## 💡 Tips

1. **Logs en tiempo real**: Usa `./ver_logs_directo.sh` o `./ver_logs_filtrados.sh`
2. **Buscar errores específicos**: `sudo journalctl -u gunicorn-controlbovino | grep "collar_id"`
3. **Ver logs por fecha**: `sudo journalctl -u gunicorn-controlbovino --since "2026-01-14 22:00:00"`
4. **Exportar logs**: `sudo journalctl -u gunicorn-controlbovino > logs_export.txt`

## 🎨 Símbolos Usados

- ✅ - Operación exitosa
- ❌ - Error
- ⚠️ - Advertencia
- ✓ - Paso completado
- 🔍 - Búsqueda

---

**Última actualización**: 14 de enero 2026
