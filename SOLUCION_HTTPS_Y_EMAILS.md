# Solución de Problemas HTTPS y URLs en Emails

## Problema 1: Error "You're accessing the development server over HTTPS, but it only supports HTTP"

### Causa
El cliente accede al servidor a través de HTTPS, pero Django recibe las peticiones en HTTP desde nginx. Django no detecta correctamente que el protocolo original era HTTPS.

### Solución Implementada

#### 1. **Configuración en Django (settings.py)**
✅ Agregadas variables:
```python
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PROTO = True  # Nueva línea
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

#### 2. **Configuración en Nginx**
✅ Actualizado `/Backend/deploy/nginx-controlbovino.conf`:
```nginx
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Port $server_port;
```

Esto asegura que nginx envíe a Django:
- `X-Forwarded-Proto: https` (cuando el cliente usa HTTPS)
- `X-Forwarded-Host: pmonitunl.vercel.app` (el dominio correcto)

---

## Problema 2: URLs en Emails con IP:Puerto en lugar de Dominio

### Causa
El código usaba `request.META.get('HTTP_HOST')` que toma el host tal como llega del navegador/cliente.
Cuando el cliente accede con IP:puerto, eso es lo que se guarda en el email.

### Solución Implementada

#### 1. **Nuevo archivo de configuración (.env)**
✅ Creado `/Backend/.env` con:
```
SITE_DOMAIN=pmonitunl.vercel.app
ALLOWED_EMAIL_DOMAIN=pmonitunl.vercel.app
```

#### 2. **Configuración en Django (settings.py)**
✅ Agregadas variables:
```python
ALLOWED_EMAIL_DOMAIN = os.environ.get('ALLOWED_EMAIL_DOMAIN', 'pmonitunl.vercel.app')
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'pmonitunl.vercel.app')
```

#### 3. **Código de Emails (users_views.py)**
✅ Modificado `CustomPasswordResetView` para usar:
```python
# Usar el dominio configurado en settings en lugar de HTTP_HOST
domain = settings.SITE_DOMAIN
protocol = 'https'  # Siempre usar HTTPS para enlaces de email
```

Ahora los emails usarán siempre:
```
https://pmonitunl.vercel.app/reset-password/confirm/MQ/d3gw45...
```

En lugar de:
```
https://190.96.102.30:3000/reset-password/confirm/MQ/d3gw45...
```

---

## Pasos Para Implementar

### Paso 1: Actualizar Variables de Entorno
En tu servidor, establece las variables (o en el archivo `.env`):

```bash
export SITE_DOMAIN="pmonitunl.vercel.app"
export ALLOWED_EMAIL_DOMAIN="pmonitunl.vercel.app"
export DEBUG="False"
```

### Paso 2: Reiniciar los Servicios

```bash
# Reiniciar nginx
sudo systemctl restart nginx

# Reiniciar gunicorn (si usas systemd)
sudo systemctl restart gunicorn-controlbovino

# O si usas PM2
pm2 restart all
```

### Paso 3: Verificar Cambios

1. **Prueba de Email**:
   - Ve a la página de reset de contraseña
   - Solicita un reset
   - Verifica que el email llegue con la URL correcta

2. **Prueba de HTTPS**:
   - Accede a través de HTTPS
   - Verifica en los logs que no hay errores de protocolo

```bash
tail -f /home/administrador/ControlBovinoVFinal/Backend/logs/error.log
```

---

## Configuración Completa de Nginx (Recomendada)

Si usas SSL/TLS (HTTPS en nginx), considera esta configuración completa:

```nginx
server {
    # Redirigir HTTP a HTTPS
    listen 190.96.102.30:8080;
    server_name 190.96.102.30;
    return 301 https://$host$request_uri;
}

server {
    # Servidor HTTPS
    listen 190.96.102.30:8081 ssl http2;
    server_name 190.96.102.30;

    ssl_certificate /etc/ssl/certs/tu-certificado.crt;
    ssl_certificate_key /etc/ssl/private/tu-clave.key;

    client_max_body_size 50M;
    access_log /var/log/nginx/controlbovino.access.log;
    error_log /var/log/nginx/controlbovino.error.log;

    location = /favicon.ico { access_log off; log_not_found off; }

    # Static files
    location /static/ {
        alias /home/administrador/ControlBovinoVFinal/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /home/administrador/ControlBovinoVFinal/media/;
    }

    # Proxy a gunicorn
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;  # Siempre HTTPS al cliente
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port 8081;
        proxy_redirect off;
        proxy_pass http://unix:/run/gunicorn-controlbovino/gunicorn-controlbovino.sock;
    }
}
```

---

## Archivos Modificados

1. ✅ `/Backend/cardiaco_vaca/settings.py`
   - `USE_X_FORWARDED_PROTO = True`
   - `SITE_DOMAIN` y `ALLOWED_EMAIL_DOMAIN`
   - `CSRF_TRUSTED_ORIGINS` actualizado

2. ✅ `/Backend/temp_car/user/users_views.py`
   - Cambio en `CustomPasswordResetView` para usar `settings.SITE_DOMAIN`

3. ✅ `/Backend/deploy/nginx-controlbovino.conf`
   - Headers adicionales: `X-Forwarded-Host` y `X-Forwarded-Port`

4. ✅ `/Backend/.env`
   - Nueva configuración de dominio

---

## Próximos Pasos Recomendados

- [ ] Configurar certificado SSL/TLS en nginx si aún no está
- [ ] Cambiar `DEBUG=False` en producción
- [ ] Verificar que los emails lleguen correctamente
- [ ] Revisar logs de nginx y Django
- [ ] Hacer prueba completa de reset de contraseña

---

## Solución Rápida si Algo Falla

Si después de reiniciar aún ves el error, haz esto:

```bash
# 1. Verifica la configuración de nginx
sudo nginx -t

# 2. Recarga nginx
sudo systemctl reload nginx

# 3. Revisa el log de errores
tail -100 /home/administrador/ControlBovinoVFinal/Backend/logs/error.log

# 4. Verifica que gunicorn está corriendo
ps aux | grep gunicorn
```
