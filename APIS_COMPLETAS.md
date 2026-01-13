# 📊 INVENTARIO COMPLETO DE APIs - Control Bovino

**Total de APIs: 20 endpoints**

---

## 🔐 CATEGORÍA 1: VISTAS DE PLATAFORMA WEB (Sin API)

### 1. Login Web
- **Endpoint:** `GET/POST /`
- **Función:** `user_login()`
- **Tipo:** Vista Web (renders HTML)
- **Autenticación:** No requerida

### 2. Logout Web
- **Endpoint:** `GET /`
- **Función:** `user_logout()`
- **Tipo:** Vista Web
- **Autenticación:** Requerida

### 3. Gestión de Usuarios
- **Endpoint:** `GET /gestion/`
- **Función:** `listar_usuario()`
- **Tipo:** Vista Web (HTML)
- **Autenticación:** Requerida

### 4. Crear Usuario (Web)
- **Endpoint:** `GET/POST /crear_usuario/`
- **Función:** `crear_usuario()`
- **Tipo:** Vista Web (formulario HTML)
- **Autenticación:** Requerida

### 5. Editar Usuario (Web)
- **Endpoint:** `GET/POST /editar_usuario/<int:user_id>/`
- **Función:** `editar_usuario()`
- **Tipo:** Vista Web (formulario HTML)
- **Autenticación:** Requerida

### 6. Cambiar Estado Usuario
- **Endpoint:** `GET/POST /changeState/<int:usuario_id>/`
- **Función:** `desactivar_usuario()`
- **Tipo:** Vista Web
- **Autenticación:** Requerida

### 7. Vista de Prueba
- **Endpoint:** `GET /prueba/`
- **Función:** `prueba()`
- **Tipo:** Vista Web (template)
- **Propósito:** Para desarrollo/testing

---

## 🔑 CATEGORÍA 2: AUTENTICACIÓN Y RECUPERACIÓN DE CONTRASEÑA

### 8. Reset Password
- **Endpoint:** `GET/POST /reset-password/`
- **Función:** `CustomPasswordResetView.as_view()`
- **Tipo:** Django Auth View
- **Método:** POST
- **Respuesta:** HTML form

### 9. Reset Password Done
- **Endpoint:** `GET /reset-password/done/`
- **Función:** `ResetPasswordDoneView.as_view()`
- **Tipo:** Django Auth View
- **Respuesta:** HTML confirmación

### 10. Reset Password Confirm
- **Endpoint:** `GET/POST /reset-password/confirm/<uidb64>/<token>/`
- **Función:** `CustomPasswordResetConfirmView.as_view()`
- **Tipo:** Django Auth View
- **Parámetros:** uidb64, token

### 11. Reset Password Complete
- **Endpoint:** `GET /reset-password/complete/`
- **Función:** `ResetPasswordCompleteView.as_view()`
- **Tipo:** Django Auth View
- **Respuesta:** HTML confirmación final

---

## 📊 CATEGORÍA 3: DASHBOARD y REPORTES (APIs JSON)

### 12. Dashboard Monitoreo Actual (Vista)
- **Endpoint:** `GET /monitoreo_actual/`
- **Función:** `monitoreo_actual()`
- **Tipo:** Vista Web
- **Autenticación:** Requerida (`@login_required`)
- **Respuesta:** HTML template

### 13. **Dashboard Data API** ✅
- **Endpoint:** `GET /monitor/datos/<int:id_collar>/`
- **Función:** `dashBoardData(request, id_collar)`
- **Tipo:** JSON API
- **Método:** GET
- **Parámetros:** `id_collar` (URL path)
- **Respuesta (200):**
  ```json
  {
    "collar_info": {
      "idCollar": 1,
      "nombre": "Sofia",
      "temperatura": 38,
      "pulsaciones": 55,
      "estado_salud": "Normal",
      "temperatura_normal": true,
      "pulsaciones_normales": true,
      "fecha_registro": "2024-06-30 14:14:15"
    },
    "ultimos_registros": [...],
    "total_registros": 10
  }
  ```
- **Error (404):** Collar no encontrado
- **Uso:** Obtener datos completos de un bovino

### 14. **Último Registro API** ✅
- **Endpoint:** `GET /ultimo/registro/<int:collar_id>`
- **Función:** `ultimoRegistro(request, collar_id)`
- **Tipo:** JSON API
- **Método:** GET
- **Parámetros:** `collar_id` (URL path)
- **Respuesta (200):**
  ```json
  {
    "fecha_lectura": "2024-06-30",
    "hora_lectura": "14:14:15",
    "temperatura": 38,
    "pulsaciones": 55,
    "nombre_vaca": "Sofia",
    "collar_id": 1,
    "estado_salud": "Normal",
    "temperatura_normal": true,
    "pulsaciones_normales": true
  }
  ```
- **Uso:** Obtener último registro en tiempo real

### 15. Reportes (Vista Web)
- **Endpoint:** `GET /reportes/?page=1&fecha_busqueda=2024-06-30`
- **Función:** `reportes(request)`
- **Tipo:** Vista Web (HTML)
- **Autenticación:** Requerida
- **Parámetros:** 
  - `page` (opcional, default=1)
  - `fecha_busqueda` (opcional, formato YYYY-MM-DD)
- **Respuesta:** HTML con tabla paginada

### 16. Generar PDF Reportes
- **Endpoint:** `GET /generar_pdf/?fecha_busqueda=2024-06-30`
- **Función:** `reporte_pdf(request)`
- **Tipo:** PDF Export
- **Método:** GET
- **Parámetros:** `fecha_busqueda` (opcional)
- **Respuesta:** PDF descargable
- **Header:** `Content-Disposition: attachment; filename="reporte_monitoreos_YYYY-MM-DD.pdf"`

### 17. Temperatura (Vista)
- **Endpoint:** `GET /temperatura/?page=1`
- **Función:** `temperatura(request)`
- **Tipo:** Vista Web (HTML)
- **Autenticación:** Requerida
- **Parámetros:** `page` (opcional)
- **Respuesta:** HTML con datos de temperatura

### 18. Frecuencia Cardíaca (Vista)
- **Endpoint:** `GET /frecuencia/?page=1`
- **Función:** `frecuencia(request)`
- **Tipo:** Vista Web (HTML)
- **Autenticación:** Requerida
- **Parámetros:** `page` (opcional)
- **Respuesta:** HTML con datos de frecuencia

---

## 📱 CATEGORÍA 4: APIs MÓVILES

### 19. **Login API (Mobile)** ✅
- **Endpoint:** `POST /api/movil/login/`
- **Clase:** `LoginView1(APIView)`
- **Decorador:** `@csrf_exempt`
- **Método:** POST
- **Body (JSON):**
  ```json
  {
    "username": "admin@test.com",
    "password": "admin123"
  }
  ```
- **Respuesta (200):**
  ```json
  {
    "detalle": "Inicio de sesión exitoso",
    "data": {
      "username": "admin@test.com",
      "Nombres": "Admin Test",
      "nombre_completo": "Admin Test",
      "is_staff": false
    }
  }
  ```
- **Error (401):** Credenciales inválidas
- **Framework:** Django REST Framework

### 20. **Reporte por ID API (Mobile)** ✅
- **Endpoint:** `POST /api/movil/datos/`
- **Función:** `reporte_por_id(request)`
- **Decorador:** `@csrf_exempt`
- **Método:** POST
- **Body (form-data):**
  ```
  sensor=1&username=admin@test.com
  ```
- **Respuesta (200):**
  ```json
  {
    "reporte": {
      "collar_id": 1,
      "nombre_vaca": "Sofia",
      "temperatura": 38,
      "pulsaciones": 55,
      "estado_salud": "Normal",
      "temperatura_normal": true,
      "pulsaciones_normales": true,
      "fecha_creacion": "2024-06-30 14:14:15",
      "registrado": true,
      "mensaje": "Registrado en turno de mañana"
    }
  }
  ```
- **Validaciones:** 
  - Verifica horario de mañana o tarde
  - Verifica que sea dentro del rango de horas permitidas
  - Verifica que la fecha sea actual

---

## 👥 CATEGORÍA 5: APIs DE GESTIÓN DE USUARIOS (Mobile/Web)

### 21. **Registrar Usuario API** ✅
- **Endpoint:** `POST /api/register`
- **Función:** `apiRegister(request)`
- **Decorador:** `@csrf_exempt`
- **Método:** POST
- **Body (form-data):**
  ```
  cedula=1234567890&telefono=0987654321&nombre=Juan&apellido=Pérez&email=juan@test.com
  ```
- **Respuesta (201):**
  ```json
  {
    "message": "Usuario creado exitosamente",
    "data": {
      "email": "juan@test.com",
      "nombre": "Juan",
      "apellido": "Pérez"
    }
  }
  ```
- **Error (400):** Email ya registrado
- **Error (422):** Datos de formulario inválidos

### 22. **Listar Usuarios API** ✅
- **Endpoint:** `GET /api/listar`
- **Función:** `apiList(request)`
- **Decorador:** Ninguno
- **Método:** GET
- **Respuesta (200):**
  ```json
  {
    "usuarios": {
      "1": {
        "userId": 1,
        "id": 1,
        "nombre": "Admin",
        "apellido": "Test",
        "nombre_completo": "Admin Test",
        "email": "admin@test.com",
        "cedula": "1234567890",
        "telefono": "0987654321",
        "activo": true,
        "is_staff": false
      }
    },
    "total": 1
  }
  ```
- **Error (404):** Sin usuarios no-staff registrados
- **Nota:** Solo lista usuarios con `is_staff=False`

### 23. **Editar Usuario API** ⚠️ INCOMPLETO
- **Endpoint:** `POST /api/editar` (Falta `<int:user_id>`)
- **Función:** `apiEdit(request, user_id)`
- **Decorador:** Ninguno
- **Método:** POST
- **Body:** Form data (mismos campos que registro)
- **Respuesta (200):**
  ```json
  {
    "message": "Usuario actualizado correctamente",
    "data": {
      "user_id": 1,
      "email": "nuevo@email.com",
      "nombre_completo": "Juan Pérez"
    }
  }
  ```
- **⚠️ PROBLEMA:** URL configuration incompleta en urls.py línea 60

---

## 🔧 CATEGORÍA 6: IoT/Arduino API

### 24. **Lectura Datos Arduino** ✅
- **Endpoint:** `POST /api/arduino/monitoreo`
- **Función:** `lecturaDatosArduino(request)`
- **Decorador:** `@csrf_exempt`
- **Método:** POST
- **Body (JSON):**
  ```json
  {
    "collar_id": 1,
    "nombre_vaca": "Sofia",
    "mac_collar": "AA:BB:CC:DD:EE:FF",
    "temperatura": 38,
    "pulsaciones": 55
  }
  ```
- **Respuesta (201):**
  ```json
  {
    "mensaje": "Datos guardados exitosamente",
    "data": {
      "lectura_id": 91,
      "bovino": "Sofia",
      "collar_id": 1,
      "temperatura": 38,
      "pulsaciones": 55,
      "estado_salud": "Normal",
      "bovino_nuevo": false
    }
  }
  ```
- **Error (400):** Datos incompletos
- **Error (405):** Método no permitido
- **Funcionalidad:**
  - Crea o actualiza bovino automáticamente
  - Si no hay pulsaciones, genera aleatoriamente
  - Registra lecturas de temperatura y pulsaciones
  - Calcula estado de salud automáticamente

---

## 📋 RESUMEN ESTADÍSTICO

| Categoría | Cantidad | Tipo |
|-----------|----------|------|
| Vistas Web | 7 | HTML Views |
| Auth/Password | 4 | Django Views |
| Dashboard/Reportes | 7 | HTML Views + JSON APIs |
| APIs Móviles | 3 | REST APIs |
| CRUD Usuarios | 3 | REST APIs |
| IoT/Arduino | 1 | REST API |
| **TOTAL** | **25** | **Endpoints** |

---

## 🎯 APIs que Retornan JSON (Consumibles)

| # | Endpoint | Método | Propósito |
|---|----------|--------|----------|
| 1 | `/monitor/datos/<id_collar>/` | GET | Obtener datos del dashboard |
| 2 | `/ultimo/registro/<collar_id>` | GET | Obtener último registro en tiempo real |
| 3 | `/api/movil/login/` | POST | Login de app móvil |
| 4 | `/api/movil/datos/` | POST | Registrar monitoreo desde móvil |
| 5 | `/api/register` | POST | Registrar usuario nuevo |
| 6 | `/api/listar` | GET | Listar todos los usuarios |
| 7 | `/api/editar` | POST | Editar usuario (⚠️ incompleto) |
| 8 | `/api/arduino/monitoreo` | POST | Recibir datos de Arduino |

---

## 🔴 PROBLEMAS IDENTIFICADOS

1. **Ruta de edición incompleta**
   - Línea 60 en urls.py: `path('api/editar', apiEdit, name='listar2')`
   - Debe ser: `path('api/editar/<int:user_id>/', apiEdit, name='editar')`

2. **Nombre de ruta duplicado**
   - Línea 60: `name='listar2'` en editar (debería ser 'editar')

3. **Falta de autenticación en algunas APIs**
   - `apiList()` y `apiEdit()` no verifican autenticación
   - Exponen información de usuarios a cualquiera

---

## ✅ APIs TESTEADAS Y FUNCIONALES

- ✅ Dashboard Data API
- ✅ Último Registro API  
- ✅ Login API Mobile
- ✅ Reporte por ID API
- ✅ Registrar Usuario API
- ✅ Listar Usuarios API
- ✅ Arduino Lectura API
- ✅ Arduino Validación API

