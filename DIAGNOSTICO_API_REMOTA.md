# 🔧 DIAGNÓSTICO Y CORRECCIONES - API REMOTA

## Problemas Detectados en las Pruebas Remotas

### 1️⃣ Arduino Data API - Error: idCollar esperaba número
**Endpoint:** `POST /api/arduino/monitoreo`
**Problema:** `Field 'idCollar' expected a number but got 'COL001'.`
**Causa:** El collar_id debe ser un número entero, no una cadena
**Solución:** Validar que collar_id sea convertible a int o especificar que puede ser string

```python
# ANTES (Línea 817):
collar_id = lecturaDecoded.get('collar_id')  # String "COL001"

bovino, creado = Bovinos.objects.get_or_create(
    idCollar=collar_id,  # ❌ Error: espera int
    ...
)

# DESPUÉS:
collar_id = lecturaDecoded.get('collar_id')
try:
    collar_id = int(collar_id)  # Convertir a int
except (ValueError, TypeError):
    return JsonResponse({
        'error': 'collar_id inválido',
        'detalle': 'collar_id debe ser un número entero'
    }, status=400)

bovino, creado = Bovinos.objects.get_or_create(
    idCollar=collar_id,  # ✅ Ahora es int
    ...
)
```

---

### 2️⃣ Mobile Reporte API - Validación JSON vs POST
**Endpoint:** `POST /api/movil/datos/`
**Problema:** Lee de `request.POST` pero el cliente envía JSON
**Causa:** `request.POST` solo funciona con form-data, no con JSON
**Solución:** Cambiar a `json.loads(request.body)`

```python
# ANTES (Línea 507):
collar_id = request.POST.get('sensor')  # ❌ POST es FormData
username = request.POST.get('username')  # ❌ Siempre None

# DESPUÉS:
try:
    data = json.loads(request.body)
except json.JSONDecodeError:
    return JsonResponse({
        'error': 'JSON inválido',
        'detalle': 'El body debe ser JSON válido'
    }, status=400)

collar_id = data.get('sensor')  # ✅ JSON
username = data.get('username')  # ✅ JSON
```

---

### 3️⃣ Register API - Problema con username
**Endpoint:** `POST /api/register`
**Problema:** Error `The given username must be set`
**Causa:** El formulario envía JSON pero apiRegister espera form-data
**Solución:** Cambiar a lectura de JSON y validación correcta

```python
# ANTES (Línea 608):
form = PersonalInfoForm(request.POST)  # ❌ Espera form-data

# DESPUÉS:
try:
    data = json.loads(request.body)
except json.JSONDecodeError:
    return JsonResponse({
        'error': 'JSON inválido',
        'detalle': 'El body debe ser JSON válido'
    }, status=400)

# Validar datos manualmente
required_fields = ['username', 'email', 'cedula', 'telefono', 'nombre', 'apellido']
if not all(field in data for field in required_fields):
    return JsonResponse({
        'error': 'Campos requeridos incompletos',
        'detalle': f'Se requieren: {", ".join(required_fields)}'
    }, status=400)
```

---

### 4️⃣ Mobile Login API - Credenciales válidas
**Endpoint:** `POST /api/movil/login/`
**Status:** 401 - Esperado
**Causa:** Las credenciales de prueba no son correctas
**Nota:** Este endpoint funciona correctamente, solo necesita credenciales válidas

---

### 5️⃣ CORS - Está Configurado ✅
**Status:** Headers correctos detectados
**Access-Control-Allow-Origin:** `*`
**Estado:** FUNCIONA CORRECTAMENTE

---

## Resumen de Cambios Necesarios

| Función | Línea | Cambio | Prioridad |
|---------|-------|--------|-----------|
| `lecturaDatosArduino` | 817 | Convertir collar_id a int | 🔴 ALTA |
| `reporte_por_id` | 507 | Cambiar a JSON en lugar de POST | 🔴 ALTA |
| `apiRegister` | 608 | Cambiar a JSON en lugar de POST | 🔴 ALTA |
| `LoginView1` | - | ✅ Funciona correctamente | Verde |
| CORS | - | ✅ Configurado correctamente | Verde |
| Dashboard | - | ✅ Funciona correctamente | Verde |

---

## Valores de Prueba Corregidos

### Arduino Data API
```json
{
  "collar_id": 1,  // ✅ Número entero
  "nombre_vaca": "Vaca Sofia",
  "mac_collar": "AA:BB:CC:DD:EE:FF",
  "temperatura": 38.5,
  "pulsaciones": 72
}
```

### Mobile Reporte API
```json
{
  "sensor": 1,  // ✅ Número entero
  "username": "lorena.sarango",
  "temperatura": 38.5,
  "pulsaciones": 72,
  "observaciones": "Prueba desde Vercel"
}
```

### User Register API
```json
{
  "username": "nuevo_usuario",
  "email": "nuevo@example.com",
  "cedula": "1234567890",
  "telefono": "0999999999",
  "nombre": "Juan",
  "apellido": "Perez"
}
```

---

## Próximas Acciones

1. ✅ Aplicar correcciones en `temp_car/views.py`
2. ✅ Ejecutar pruebas remotas nuevamente
3. ✅ Validar que todos los endpoints pasen
4. ✅ Crear script de prueba final con valores correctos

