# 🧪 Guía de Verificación - Sistema de Turnos

**Documento:** Instrucciones para verificar que el sistema de turnos funciona correctamente  
**Última Actualización:** 15 de Enero de 2026  
**Estado:** ✅ Sistema validado

---

## 📋 Verificaciones Rápidas

### 1. Verificar que el Servidor está Online

```bash
pm2 status | grep django-app
```

**Esperado:**
```
│ 8  │ django-app │ default │ N/A  │ fork │ 1723590 │ 5m │ 2 │ online │ 0% │ 24.1mb │
```

---

### 2. Verificar la Base de Datos

```bash
cd /home/administrador/ControlBovinoVFinal/Backend

python manage.py shell << 'EOF'
from temp_car.models import Bovinos, ControlMonitoreo
from django.utils import timezone

# Listar bovinos disponibles
bovinos = Bovinos.objects.filter(activo=True)
print("Bovinos disponibles:")
for b in bovinos:
    print(f"  - Collar {b.idCollar}: {b.nombre}")

# Verificar registros de hoy
hoy = timezone.now().date()
registros = ControlMonitoreo.objects.filter(fecha_lectura=hoy).count()
print(f"\nRegistros de {hoy}: {registros}")
EOF
```

---

## 🧪 Pruebas Manuales

### Test 1: Primer Registro (Debe Aceptarse)

```bash
curl -X POST http://localhost:8081/api/movil/datos/ \
  -H "Content-Type: application/json" \
  -d '{"sensor": 1, "username": "baherreram@gmail.com"}' | jq '.'
```

**Esperado:**
```json
{
  "reporte": {
    "registrado": true,
    "mensaje": "Registrado en turno de [mañana|tarde|noche]"
  }
}
```

---

### Test 2: Segundo Intento Duplicado (Debe Bloquearse)

```bash
curl -X POST http://localhost:8081/api/movil/datos/ \
  -H "Content-Type: application/json" \
  -d '{"sensor": 1, "username": "baherreram@gmail.com"}' | jq '.'
```

**Esperado:**
```json
{
  "reporte": {
    "registrado": false,
    "mensaje": "Ya registrado en turno de [mañana|tarde|noche]"
  }
}
```

---

### Test 3: Múltiples Intentos

Ejecutar el Test 2 varias veces. Todos deben retornar `"registrado": false` con el mismo mensaje.

---

## 🔍 Verificación en la BD

### Ver Registros de Hoy

```bash
cd /home/administrador/ControlBovinoVFinal/Backend

python manage.py shell << 'EOF'
from temp_car.models import ControlMonitoreo, Lectura
from django.utils import timezone
from datetime import time

hoy = timezone.now().date()

# Todos los registros de hoy
todos = ControlMonitoreo.objects.filter(fecha_lectura=hoy).count()
print(f"Total registros de {hoy}: {todos}")

# Por turno
manana = ControlMonitoreo.objects.filter(
    fecha_lectura=hoy,
    hora_lectura__range=(time(7,0), time(12,0))
).count()

tarde = ControlMonitoreo.objects.filter(
    fecha_lectura=hoy,
    hora_lectura__range=(time(12,0), time(18,0))
).count()

noche = ControlMonitoreo.objects.filter(
    fecha_lectura=hoy,
    hora_lectura__range=(time(18,0), time(23,59))
).count()

print(f"  - Mañana (7-12): {manana}")
print(f"  - Tarde (12-18): {tarde}")
print(f"  - Noche (18-00): {noche}")
EOF
```

**Esperado:** Máximo 1 por turno (máximo 3 total)

---

## 📊 Validación de Rangos Horarios

### Verificar Configuración de Turnos

```bash
cd /home/administrador/ControlBovinoVFinal/Backend

python manage.py shell << 'EOF'
from temp_car.utils.monitorChecking import (
    startMorning, endMorning,
    startAfternoon, endAfternoon,
    startNight, endNight
)

print("Rangos de Turnos:")
print(f"  Mañana:   {startMorning.time()} - {endMorning.time()}")
print(f"  Tarde:    {startAfternoon.time()} - {endAfternoon.time()}")
print(f"  Noche:    {startNight.time()} - {endNight.time()}")
EOF
```

**Esperado:**
```
Rangos de Turnos:
  Mañana:   07:00:00 - 12:00:00
  Tarde:    12:00:00 - 18:00:00
  Noche:    18:00:00 - 23:59:00
```

---

## 🔧 Resetear Registros de Hoy

Si necesitas limpiar los registros para hacer nuevas pruebas:

```bash
cd /home/administrador/ControlBovinoVFinal/Backend

python manage.py shell << 'EOF'
from temp_car.models import ControlMonitoreo, Bovinos
from django.utils import timezone

hoy = timezone.now().date()
bovino = Bovinos.objects.get(idCollar=1)

# Eliminar registros de hoy para este bovino
ControlMonitoreo.objects.filter(
    id_Lectura__id_Bovino=bovino,
    fecha_lectura=hoy
).delete()

print(f"✓ Registros de {bovino.nombre} ({hoy}) eliminados")
EOF
```

---

## ⚠️ Solución de Problemas

### Problema: El servidor retorna 404

**Solución:**
```bash
pm2 restart django-app --no-autorestart
```

---

### Problema: Las pruebas muestran mensaje antiguo

**Solución:**
Reiniciar el servidor para recargar el código:
```bash
pm2 restart django-app --no-autorestart
```

---

### Problema: Base de datos con registros antiguos

**Solución:**
Limpiar registros con el comando en "Resetear Registros de Hoy"

---

## 📱 Prueba desde App Móvil

La app móvil debe enviar POST a:

```
POST http://localhost:8081/api/movil/datos/
Content-Type: application/json

{
  "sensor": <collar_id>,
  "username": "<email_usuario>"
}
```

**Respuesta esperada:**
```json
{
  "reporte": {
    "collar_id": 1,
    "nombre_vaca": "Vaca Luna",
    "temperatura": 38,
    "pulsaciones": 85,
    "estado_salud": "Alerta",
    "temperatura_normal": true,
    "pulsaciones_normales": false,
    "fecha_creacion": "2026-01-15 20:00:00",
    "registrado": true,
    "mensaje": "Registrado en turno de noche"
  }
}
```

---

## ✅ Checklist de Validación

- [ ] Servidor Django online (PM2)
- [ ] Puerto 8081 accesible
- [ ] Base de datos con bovinos
- [ ] Primer registro aceptado (registrado=true)
- [ ] Segundo registro bloqueado (registrado=false)
- [ ] Mensaje diferenciado: "Ya registrado..."
- [ ] Máximo 1 por turno verificado
- [ ] Máximo 3 total por día verificado
- [ ] Diferentes bovinos funcionan independiente
- [ ] Diferentes usuarios funcionan correctamente

---

## 🎯 Resultado Esperado

Después de las pruebas, el sistema debe:

1. ✅ **Aceptar** primer registro con `registrado: true`
2. ✅ **Bloquear** segundo intento con `registrado: false`
3. ✅ **Mostrar** mensaje claro: "Ya registrado en turno de X"
4. ✅ **Permitir** registro en turno diferente
5. ✅ **Bloquear** segundo registro en ese turno
6. ✅ **Máximo 3 registros totales** por día (uno por turno)

---

**✨ Sistema completamente validado y listo para producción**

Consulta los documentos:
- [IMPLEMENTACION_TURNOS_COMPLETA.md](IMPLEMENTACION_TURNOS_COMPLETA.md) - Detalles técnicos
- [Backend/TURNOS_RESUMEN.md](Backend/TURNOS_RESUMEN.md) - Resumen ejecutivo
- [IMPLEMENTACION_TURNOS_EVIDENCIA.md](IMPLEMENTACION_TURNOS_EVIDENCIA.md) - Evidencia con pruebas
