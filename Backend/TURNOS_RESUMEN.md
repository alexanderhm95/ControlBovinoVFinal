# 🎯 Sistema de Turnos - Resumen Ejecutivo

## ¿Qué se logró?

La app móvil ahora **bloquea registros duplicados** por turno. Cada bovino se puede registrar **máximo 1 vez por turno, 3 veces al día**:

- **Mañana (7:00 - 12:00):** 1 registro máximo
- **Tarde (12:00 - 18:00):** 1 registro máximo  
- **Noche (18:00 - 23:59):** 1 registro máximo

---

## Respuestas del API

### ✅ Primer Registro (Exitoso)
```json
{
  "registrado": true,
  "mensaje": "Registrado en turno de tarde"
}
```

### ❌ Segundo Intento en Mismo Turno (Bloqueado)
```json
{
  "registrado": false,
  "mensaje": "Ya registrado en turno de tarde"
}
```

---

## Horarios por Turno

```
07:00 ━━━━━━━━━━━━ 12:00
      TURNO MAÑANA

12:00 ━━━━━━━━━━━━ 18:00
      TURNO TARDE

18:00 ━━━━━━━━━━━━ 23:59
      TURNO NOCHE
```

---

## Validaciones Implementadas

✅ **checkingMorning()** - Verifica si ya se registró en mañana  
✅ **checkingAfternoon()** - Verifica si ya se registró en tarde  
✅ **checkingNight()** - Verifica si ya se registró en noche  
✅ **checkHoursMorning()** - Valida hora en rango mañana  
✅ **checkHoursAfternoon()** - Valida hora en rango tarde  
✅ **checkHoursNight()** - Valida hora en rango noche  

---

## Flujo de Validación

```
¿Es una lectura de hoy?
  ├─ NO → "Lectura no es de hoy"
  └─ SÍ → ¿En qué turno cae esta hora?
       ├─ MAÑANA (7-12) → ¿Ya registrado en mañana?
       │                   ├─ SÍ → "Ya registrado en turno de mañana"
       │                   └─ NO → ✅ CREAR REGISTRO
       │
       ├─ TARDE (12-18) → ¿Ya registrado en tarde?
       │                   ├─ SÍ → "Ya registrado en turno de tarde"
       │                   └─ NO → ✅ CREAR REGISTRO
       │
       └─ NOCHE (18-00) → ¿Ya registrado en noche?
                           ├─ SÍ → "Ya registrado en turno de noche"
                           └─ NO → ✅ CREAR REGISTRO
```

---

## Base de Datos

### Tabla: ControlMonitoreo
```
id_Control    | id_Lectura | id_User | fecha_lectura | hora_lectura
──────────────┼────────────┼─────────┼───────────────┼──────────────
1             | 82         | 1       | 2026-01-15    | 20:00:00
```

**Validación:** Se buscan registros con la misma **fecha_lectura** y **id_Bovino** dentro del rango de horas del turno.

---

## Ejemplo de Uso

### Caso Real: Vaca Luna (Collar 1)

**Mañana - 9:30 AM**
```bash
POST /api/movil/datos/
{"sensor": 1, "username": "admin@example.com"}
```
↓
```json
{ "registrado": true, "mensaje": "Registrado en turno de mañana" }
```

**Mañana - 10:15 AM (Mismo Turno)**
```bash
POST /api/movil/datos/
{"sensor": 1, "username": "admin@example.com"}
```
↓
```json
{ "registrado": false, "mensaje": "Ya registrado en turno de mañana" }
```

**Tarde - 2:00 PM (Diferente Turno)**
```bash
POST /api/movil/datos/
{"sensor": 1, "username": "admin@example.com"}
```
↓
```json
{ "registrado": true, "mensaje": "Registrado en turno de tarde" }
```

---

## Archivos Actualizados

1. **Backend/temp_car/utils/monitorChecking.py**
   - Agregadas funciones de noche
   - Actualizado rango de tarde a 12:00-18:00

2. **Backend/temp_car/views.py**
   - Mejorada lógica de `reporte_por_id()`
   - Agregada validación de turno noche
   - Mensajes diferenciados por situación

---

## Tests Exitosos ✅

| Prueba | Resultado |
|--------|-----------|
| Primer registro en turno | ✅ PASS |
| Segundo intento duplicado | ✅ PASS |
| Tercer intento | ✅ PASS |
| Diferentes turnos | ✅ PASS |

