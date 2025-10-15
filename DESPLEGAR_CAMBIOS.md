# 🚀 Guía de Despliegue de Cambios a Fly.io

**Fecha:** 15 de octubre de 2025  
**Proyecto:** Control Bovino VFinal

---

## ✅ Estado Actual

Los cambios realizados incluyen:
- ✅ Mejoras en `models.py`
- ✅ Migraciones aplicadas localmente
- ✅ Mejoras en `views.py`
- ✅ Mejoras en `users_views.py`
- ✅ Mejoras en `forms.py`
- ✅ Mejoras en `admin.py`

**IMPORTANTE:** Estos cambios están solo en tu máquina local. Fly.io no los tiene aún.

---

## 📋 Pasos para Desplegar a Fly.io

### **Paso 1: Verificar Estado de Git** ✅

Primero verifica que todos tus cambios estén commiteados:

```powershell
git status
```

**Resultado esperado:**
```
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

✅ **Tu estado actual: LISTO** - Ya tienes todo commiteado

---

### **Paso 2: Hacer Push a GitHub** (Opcional pero recomendado)

Aunque no es necesario para Fly.io, es buena práctica tener tu código en GitHub:

```powershell
git push origin main
```

Esto sube tus cambios al repositorio remoto.

---

### **Paso 3: Desplegar a Fly.io** 🚀

Fly.io desplegará desde tu código local. Ejecuta:

```powershell
flyctl deploy
```

**¿Qué hace este comando?**
1. 📦 Empaqueta tu código actual
2. 🏗️ Construye la imagen Docker
3. 📤 Sube la imagen a Fly.io
4. 🔄 Actualiza la aplicación
5. 🗄️ **Ejecuta las migraciones pendientes**
6. ✅ Reinicia los servicios

---

### **Paso 4: Verificar el Despliegue**

#### **4.1 Ver logs en tiempo real:**

```powershell
flyctl logs
```

Busca mensajes como:
```
✓ Applying migrations...
✓ Running temp_car.0005_alter_bovinos_options...
✓ Deployment successful
```

#### **4.2 Verificar migraciones:**

```powershell
flyctl ssh console
python manage.py showmigrations
```

Deberías ver:
```
temp_car
 [X] 0001_initial
 [X] 0002_initial
 [X] 0003_delete_medicioncompleto
 [X] 0004_controlmonitoreo
 [X] 0005_alter_bovinos_options_alter_controlmonitoreo_options_and_more  ← NUEVA
```

#### **4.3 Acceder a tu aplicación:**

```powershell
flyctl open
```

O visita: `https://tu-app.fly.dev`

---

## 🔍 ¿Cómo Saber si las Mejoras Están Activas?

### **Opción 1: Verificar en el Admin de Django**

1. Accede al admin: `https://tu-app.fly.dev/admin`
2. Ve a la sección de **Bovinos**
3. **Verifica:**
   - ✅ Debe haber un campo nuevo "Activo" con checkboxes verdes/rojos
   - ✅ Los collares deben mostrar badges de estado
   - ✅ Las lecturas deben mostrar estado de salud (Normal/Alerta/Crítico)
   - ✅ Los colores en temperatura y pulsaciones

### **Opción 2: Verificar Modelos en la Base de Datos**

```powershell
flyctl ssh console
python manage.py shell
```

Luego en el shell:
```python
from temp_car.models import Bovinos, Lectura

# Verificar campo nuevo 'activo'
bovino = Bovinos.objects.first()
print(bovino.activo)  # Debe existir

# Verificar propiedades nuevas
lectura = Lectura.objects.first()
print(lectura.estado_salud)  # Debe retornar: Normal, Alerta o Crítico
print(lectura.temperatura_normal)  # True o False
```

### **Opción 3: Probar API desde la App Móvil**

Las APIs ahora retornan más información:

```json
{
  "reporte": {
    "collar_id": 1,
    "nombre_vaca": "Vaca 1",
    "temperatura": 38,
    "pulsaciones": 70,
    "estado_salud": "Normal",           ← NUEVO
    "temperatura_normal": true,          ← NUEVO
    "pulsaciones_normales": true,        ← NUEVO
    "mensaje": "Registrado en turno de mañana"  ← NUEVO
  }
}
```

---

## ⚠️ Problemas Comunes y Soluciones

### **Error: "Module not found: xhtml2pdf"**

**Solución:**
```powershell
# Asegúrate que esté en requirements.txt
flyctl deploy
```

### **Error: "No changes to deploy"**

**Causa:** Fly.io detecta que no hay cambios desde el último despliegue

**Solución:**
```powershell
# Forzar redespliegue
flyctl deploy --force
```

### **Error en Migraciones**

**Ver logs específicos:**
```powershell
flyctl logs --app tu-app-name
```

**Ejecutar migraciones manualmente:**
```powershell
flyctl ssh console
python manage.py migrate
```

### **Base de datos no actualizada**

**Verificar estado:**
```powershell
flyctl ssh console
python manage.py showmigrations
```

**Aplicar migraciones pendientes:**
```powershell
python manage.py migrate
```

---

## 📝 Comandos Útiles de Fly.io

### **Ver información de la app:**
```powershell
flyctl status
```

### **Ver logs en tiempo real:**
```powershell
flyctl logs
```

### **Acceder a la consola:**
```powershell
flyctl ssh console
```

### **Ver variables de entorno:**
```powershell
flyctl secrets list
```

### **Escalar la aplicación:**
```powershell
flyctl scale count 2  # Dos instancias
```

### **Ver métricas:**
```powershell
flyctl dashboard
```

### **Abrir la app en el navegador:**
```powershell
flyctl open
```

---

## 🔄 Flujo Completo de Trabajo

### **Para Cambios Locales → Producción:**

```powershell
# 1. Hacer cambios en código local
# 2. Probar localmente
python manage.py runserver

# 3. Aplicar migraciones locales
python manage.py makemigrations
python manage.py migrate

# 4. Commit cambios
git add .
git commit -m "Mejoras en modelos, views y forms"

# 5. Push a GitHub (opcional)
git push origin main

# 6. Desplegar a Fly.io
flyctl deploy

# 7. Verificar
flyctl logs
flyctl open
```

---

## ✅ Checklist de Despliegue

Antes de desplegar, verifica:

- [ ] `python manage.py check` sin errores
- [ ] `python manage.py makemigrations` ejecutado
- [ ] `python manage.py migrate` ejecutado localmente
- [ ] Cambios commiteados en git
- [ ] `requirements.txt` actualizado con nuevas dependencias
- [ ] Probar localmente con `runserver`

Durante el despliegue:

- [ ] `flyctl deploy` ejecutado
- [ ] Sin errores en la salida del comando
- [ ] Migraciones aplicadas en Fly.io

Después del despliegue:

- [ ] `flyctl logs` sin errores
- [ ] Admin de Django muestra nuevos campos
- [ ] APIs retornan nueva estructura
- [ ] App móvil funciona correctamente

---

## 🎯 Resumen Rápido

**Para desplegar tus cambios:**

```powershell
# Comando principal
flyctl deploy

# Verificar
flyctl logs
flyctl open

# Si hay problemas
flyctl ssh console
python manage.py migrate
```

**¿Cuándo desplegar?**
- ✅ Después de cada cambio importante
- ✅ Después de agregar nuevas funcionalidades
- ✅ Después de crear migraciones
- ✅ Después de actualizar dependencias

**¿Cuánto tarda?**
- ⏱️ 2-5 minutos en promedio
- Depende del tamaño de la imagen Docker

---

## 📞 Soporte

Si tienes problemas:

1. **Ver logs:** `flyctl logs`
2. **Documentación:** https://fly.io/docs/
3. **Community:** https://community.fly.io/

---

**¡Listo para desplegar!** 🚀

Ejecuta: `flyctl deploy` y verás tus mejoras en producción en unos minutos.
