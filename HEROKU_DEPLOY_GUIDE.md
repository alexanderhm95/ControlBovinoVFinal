# 🚀 Guía de Despliegue en Heroku

Esta guía te ayudará a desplegar tu aplicación Django de Control Bovino en Heroku.

## 📋 Prerequisitos

1. **Cuenta de Heroku**: Crea una cuenta gratuita en [heroku.com](https://heroku.com)
2. **Heroku CLI**: Instala el CLI de Heroku desde [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Asegúrate de tener Git instalado

## 🔧 Archivos ya Configurados

Los siguientes archivos ya están configurados en tu proyecto:

- ✅ `runtime.txt` - Especifica Python 3.13.3
- ✅ `Procfile` - Define cómo iniciar la aplicación
- ✅ `requirements.txt` - Lista todas las dependencias
- ✅ `settings.py` - Configurado para Heroku con:
  - ALLOWED_HOSTS incluye `.herokuapp.com`
  - CSRF_TRUSTED_ORIGINS incluye `https://*.herokuapp.com`
  - Configuración de base de datos PostgreSQL mediante `DATABASE_URL`
  - WhiteNoise para servir archivos estáticos

## 📝 Pasos para el Despliegue

### 1. Instalar Heroku CLI

En PowerShell, ejecuta:
```powershell
# Verifica si Heroku CLI está instalado
heroku --version
```

Si no está instalado, descárgalo desde: https://devcenter.heroku.com/articles/heroku-cli

### 2. Iniciar Sesión en Heroku

```powershell
heroku login
```

Esto abrirá tu navegador para autenticarte.

### 3. Crear la Aplicación en Heroku

```powershell
# Crea una nueva app de Heroku (elige un nombre único)
heroku create nombre-de-tu-app

# O deja que Heroku genere un nombre aleatorio
heroku create
```

### 4. Agregar PostgreSQL (Base de Datos)

Heroku ofrece PostgreSQL gratuito:

```powershell
heroku addons:create heroku-postgresql:essential-0
```

Esto creará automáticamente la variable de entorno `DATABASE_URL`.

### 5. Configurar Variables de Entorno

Configura las variables de entorno necesarias:

```powershell
# SECRET_KEY - Genera una nueva clave secreta
heroku config:set SECRET_KEY="tu-clave-secreta-super-segura-aqui"

# DEBUG - En producción siempre debe ser False
heroku config:set DEBUG=False

# Si usas Azure Blob Storage (opcional)
heroku config:set AZURE_ACCOUNT_NAME="tu-cuenta-azure"
heroku config:set AZURE_ACCOUNT_KEY="tu-clave-azure"
heroku config:set AZURE_CONTAINER="staticfiles"

# Configuración de email (opcional)
heroku config:set EMAIL_HOST_USER="vacauniversidad@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="nydandvfcibguwhf"
```

**⚠️ IMPORTANTE**: Genera una nueva SECRET_KEY segura. Puedes usar:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Verificar el Repositorio Git

```powershell
# Verifica que estás en el directorio del proyecto
cd c:\Users\bherrera\Documents\GitHub\ControlBovinoVFinal

# Verifica el estado de Git
git status

# Si hay cambios, haz commit
git add .
git commit -m "Preparar aplicación para despliegue en Heroku"
```

### 7. Conectar con Heroku

```powershell
# Agrega Heroku como remoto (si no lo hiciste con heroku create)
heroku git:remote -a nombre-de-tu-app
```

### 8. Desplegar la Aplicación

```powershell
# Sube el código a Heroku
git push heroku main

# Si tu rama principal se llama 'master', usa:
# git push heroku master
```

### 9. Ejecutar Migraciones

Después del despliegue, ejecuta las migraciones:

```powershell
heroku run python manage.py migrate
```

### 10. Crear Superusuario (Opcional)

```powershell
heroku run python manage.py createsuperuser
```

### 11. Recolectar Archivos Estáticos

```powershell
heroku run python manage.py collectstatic --noinput
```

### 12. Abrir la Aplicación

```powershell
heroku open
```

## 🔍 Comandos Útiles

### Ver logs en tiempo real:
```powershell
heroku logs --tail
```

### Ver las variables de entorno configuradas:
```powershell
heroku config
```

### Escalar dynos (unidades de procesamiento):
```powershell
heroku ps:scale web=1
```

### Ver el estado de la aplicación:
```powershell
heroku ps
```

### Reiniciar la aplicación:
```powershell
heroku restart
```

### Ejecutar comandos Django:
```powershell
heroku run python manage.py <comando>
```

### Acceder a la base de datos PostgreSQL:
```powershell
heroku pg:psql
```

### Hacer backup de la base de datos:
```powershell
heroku pg:backups:capture
heroku pg:backups:download
```

## 🔄 Actualizaciones Posteriores

Cada vez que hagas cambios en tu código:

```powershell
# 1. Hacer commit de los cambios
git add .
git commit -m "Descripción de los cambios"

# 2. Subir a Heroku
git push heroku main

# 3. Si hay cambios en el modelo, ejecutar migraciones
heroku run python manage.py migrate
```

## ⚠️ Solución de Problemas

### Error: "No web processes running"
```powershell
heroku ps:scale web=1
```

### Error: "Application error"
Revisa los logs:
```powershell
heroku logs --tail
```

### Error de base de datos
Verifica que PostgreSQL esté configurado:
```powershell
heroku addons
heroku config:get DATABASE_URL
```

### Error de archivos estáticos
```powershell
heroku run python manage.py collectstatic --noinput
```

### Reiniciar la aplicación completamente
```powershell
heroku restart
```

## 📊 Plan Gratuito de Heroku

El plan gratuito "Eco" de Heroku incluye:
- 1000 horas de dyno por mes
- PostgreSQL con límite de 10,000 filas
- Aplicación duerme después de 30 minutos de inactividad
- Se despierta automáticamente al recibir tráfico

## 🔗 Enlaces Útiles

- [Documentación de Heroku](https://devcenter.heroku.com/)
- [Django en Heroku](https://devcenter.heroku.com/articles/django-app-configuration)
- [PostgreSQL en Heroku](https://devcenter.heroku.com/articles/heroku-postgresql)
- [Troubleshooting de Heroku](https://devcenter.heroku.com/articles/troubleshooting-application-logs)

## ✅ Checklist Post-Despliegue

- [ ] La aplicación se abre correctamente con `heroku open`
- [ ] Puedes acceder al panel de administración en `/admin`
- [ ] Las migraciones se ejecutaron correctamente
- [ ] Los archivos estáticos se cargan correctamente
- [ ] Puedes crear y gestionar vacas/mediciones
- [ ] Las credenciales sensibles están en variables de entorno
- [ ] DEBUG está en False en producción
- [ ] Los logs no muestran errores críticos

## 🎉 ¡Listo!

Tu aplicación de Control Bovino ahora está desplegada en Heroku. Puedes acceder a ella mediante:
```
https://nombre-de-tu-app.herokuapp.com
```

---

**Nota**: Si necesitas más dynos o una base de datos más grande, considera actualizar a los planes de pago de Heroku.
