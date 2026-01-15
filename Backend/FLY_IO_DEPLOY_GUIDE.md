# 🚀 Guía de Despliegue en Fly.io

## 📋 Tabla de Contenidos
- [Requisitos Previos](#requisitos-previos)
- [Instalación de Fly.io CLI](#instalación-de-flyio-cli)
- [Configuración Inicial](#configuración-inicial)
- [Configuración de Base de Datos](#configuración-de-base-de-datos)
- [Variables de Entorno](#variables-de-entorno)
- [Despliegue](#despliegue)
- [Verificación y Monitoreo](#verificación-y-monitoreo)
- [Solución de Problemas](#solución-de-problemas)

---

## 📦 Requisitos Previos

- Cuenta en [Fly.io](https://fly.io/app/sign-up)
- Git instalado
- Python 3.11 o superior
- Método de pago configurado en Fly.io (opcional para desarrollo)

---

## 🔧 Instalación de Fly.io CLI

### Windows (PowerShell)
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### macOS/Linux
```bash
curl -L https://fly.io/install.sh | sh
```

### Verificar instalación
```bash
flyctl version
```

---

## 🔐 Configuración Inicial

### 1. Autenticarse en Fly.io
```bash
flyctl auth login
```
Esto abrirá tu navegador para autenticarte.

### 2. Verificar archivos de configuración

Tu proyecto debe tener estos archivos:
- ✅ `Dockerfile` - Ya generado
- ✅ `fly.toml` - Ya configurado
- ✅ `.dockerignore` - Ya creado
- ✅ `requirements.txt` - Existente

---

## 🗄️ Configuración de Base de Datos

### Opción 1: PostgreSQL en Fly.io (Recomendado)

#### Crear base de datos PostgreSQL
```bash
flyctl postgres create --name control-bovino-db --region gru
```

Parámetros sugeridos:
- **Configuration**: Development (1 node, 1x shared CPU, 256MB RAM)
- **Volume size**: 1GB (suficiente para desarrollo)

#### Conectar la base de datos a la app
```bash
flyctl postgres attach control-bovino-db --app control-bovino-vfinal
```

Esto creará automáticamente la variable `DATABASE_URL`.

### Opción 2: SQLite (Solo para desarrollo/pruebas)

Si prefieres usar SQLite (no recomendado para producción):
```bash
flyctl volumes create sqlite_data --size 1 --region gru --app control-bovino-vfinal
```

Actualizar `fly.toml` agregando:
```toml
[mounts]
  source = "sqlite_data"
  destination = "/code/data"
```

---

## 🔑 Variables de Entorno

### Configurar SECRET_KEY de Django
```bash
flyctl secrets set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" --app control-bovino-vfinal
```

### Configurar DEBUG
```bash
flyctl secrets set DEBUG=False --app control-bovino-vfinal
```

### Configurar ALLOWED_HOSTS
```bash
flyctl secrets set ALLOWED_HOSTS="control-bovino-vfinal.fly.dev" --app control-bovino-vfinal
```

### Variables adicionales (si las usas)

#### Cloudinary (si usas almacenamiento en la nube)
```bash
flyctl secrets set CLOUDINARY_CLOUD_NAME="tu_cloud_name" --app control-bovino-vfinal
flyctl secrets set CLOUDINARY_API_KEY="tu_api_key" --app control-bovino-vfinal
flyctl secrets set CLOUDINARY_API_SECRET="tu_api_secret" --app control-bovino-vfinal
```

#### Azure Storage (si usas Azure)
```bash
flyctl secrets set AZURE_ACCOUNT_NAME="tu_account_name" --app control-bovino-vfinal
flyctl secrets set AZURE_ACCOUNT_KEY="tu_account_key" --app control-bovino-vfinal
flyctl secrets set AZURE_CONTAINER="tu_container" --app control-bovino-vfinal
```

### Ver todas las variables configuradas
```bash
flyctl secrets list --app control-bovino-vfinal
```

---

## 🚀 Despliegue

### 1. Verificar configuración
```bash
flyctl config validate
```

### 2. Desplegar la aplicación
```bash
flyctl deploy
```

Este comando:
- ✅ Construye la imagen Docker
- ✅ Sube la imagen a Fly.io
- ✅ Ejecuta las migraciones (si están configuradas)
- ✅ Recolecta archivos estáticos
- ✅ Inicia la aplicación

### 3. Esperar a que termine el despliegue
El proceso puede tomar 2-5 minutos.

---

## ✅ Verificación y Monitoreo

### Abrir la aplicación en el navegador
```bash
flyctl open
```

### Ver logs en tiempo real
```bash
flyctl logs
```

### Ver estado de la aplicación
```bash
flyctl status
```

### Ejecutar migraciones manualmente (si es necesario)
```bash
flyctl ssh console --app control-bovino-vfinal
python manage.py migrate
exit
```

### Crear superusuario
```bash
flyctl ssh console --app control-bovino-vfinal
python manage.py createsuperuser
exit
```

### Ver recursos utilizados
```bash
flyctl dashboard
```

---

## 🔄 Actualizaciones

### Desplegar cambios
Después de hacer cambios en tu código:

```bash
git add .
git commit -m "Descripción de cambios"
flyctl deploy
```

### Rollback a versión anterior
Si algo sale mal:
```bash
flyctl releases list
flyctl releases rollback <version_number>
```

---

## 🐛 Solución de Problemas

### Error: "unsuccessful command 'flyctl launch'"

**Solución:**
1. Actualizar Fly.io CLI:
   ```bash
   flyctl version update
   ```

2. Limpiar caché:
   ```bash
   flyctl auth token
   flyctl auth logout
   flyctl auth login
   ```

3. Reintentar con `--no-deploy`:
   ```bash
   flyctl launch --no-deploy
   ```

### Error: "failed to fetch an image or build from source"

**Solución:**
1. Verificar Dockerfile:
   ```bash
   docker build -t test-build .
   ```

2. Verificar requirements.txt (buscar versiones incompatibles)

3. Aumentar tiempo de build:
   ```bash
   flyctl deploy --build-timeout 600
   ```

### Error: "Application is not responding"

**Solución:**
1. Verificar logs:
   ```bash
   flyctl logs
   ```

2. Reiniciar la aplicación:
   ```bash
   flyctl apps restart control-bovino-vfinal
   ```

3. Verificar que ALLOWED_HOSTS incluya tu dominio:
   ```python
   # settings.py
   ALLOWED_HOSTS = ['control-bovino-vfinal.fly.dev', 'localhost', '127.0.0.1']
   ```

### Error: "Database connection failed"

**Solución:**
1. Verificar variable DATABASE_URL:
   ```bash
   flyctl secrets list
   ```

2. Verificar que la base de datos esté corriendo:
   ```bash
   flyctl postgres status --app control-bovino-db
   ```

3. Reconectar la base de datos:
   ```bash
   flyctl postgres detach control-bovino-db --app control-bovino-vfinal
   flyctl postgres attach control-bovino-db --app control-bovino-vfinal
   ```

### Error: "Out of memory"

**Solución:**
1. Aumentar memoria en `fly.toml`:
   ```toml
   [[vm]]
     memory = '2gb'  # Aumentar de 1gb a 2gb
     cpu_kind = 'shared'
     cpus = 1
   ```

2. Redesplegar:
   ```bash
   flyctl deploy
   ```

### Problema: Archivos estáticos no se cargan

**Solución:**
1. Verificar `STATIC_ROOT` en settings.py:
   ```python
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   ```

2. Verificar sección `[[statics]]` en fly.toml:
   ```toml
   [[statics]]
     guest_path = '/code/static'
     url_prefix = '/static/'
   ```

3. Usar WhiteNoise (ya está en requirements.txt):
   ```python
   # settings.py
   MIDDLEWARE = [
       # ...
       'whitenoise.middleware.WhiteNoiseMiddleware',
       # ...
   ]
   ```

---

## 📊 Comandos Útiles

### Información de la aplicación
```bash
flyctl info
```

### Escalar aplicación
```bash
# Aumentar RAM
flyctl scale memory 2048

# Aumentar CPUs
flyctl scale cpu 2

# Aumentar número de instancias
flyctl scale count 2
```

### Acceso SSH a la aplicación
```bash
flyctl ssh console
```

### Ver certificados SSL
```bash
flyctl certs list
```

### Configurar dominio personalizado
```bash
flyctl certs add tudominio.com
```

---

## 💰 Costos (Free Tier)

Fly.io ofrece:
- ✅ 3 máquinas compartidas con 256MB RAM (gratis)
- ✅ 160GB de transferencia saliente (gratis)
- ✅ 3GB de almacenamiento persistente (gratis)

**Para este proyecto en free tier:**
- 1 máquina compartida con 1GB RAM (~$5/mes)
- PostgreSQL con 256MB RAM (~$0/mes en plan desarrollo)

---

## 🔗 Referencias

- [Documentación oficial de Fly.io](https://fly.io/docs/)
- [Django en Fly.io](https://fly.io/docs/django/)
- [Fly.io CLI Reference](https://fly.io/docs/flyctl/)
- [Fly.io PostgreSQL](https://fly.io/docs/postgres/)

---

## 📝 Notas Importantes

1. **Seguridad**: Nunca commits el archivo `.env` o secretos al repositorio
2. **Backups**: Configura backups automáticos de la base de datos
3. **Monitoreo**: Revisa los logs regularmente
4. **Actualizaciones**: Mantén las dependencias actualizadas

---

## 🎯 Checklist de Despliegue

- [ ] Fly.io CLI instalado
- [ ] Autenticado en Fly.io
- [ ] Archivos de configuración creados (Dockerfile, fly.toml)
- [ ] Base de datos PostgreSQL creada y conectada
- [ ] Variables de entorno configuradas
- [ ] Despliegue exitoso
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Archivos estáticos funcionando
- [ ] Aplicación accesible en navegador
- [ ] Logs monitoreados

---

¡Listo! Tu aplicación Django debería estar corriendo en Fly.io. 🎉
