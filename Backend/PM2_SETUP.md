# PM2 Ecosystem Configuration para Control Bovino Backend

Este archivo `ecosystem.config.js` configura PM2 para gestionar el Backend Django de Control Bovino.

## Instalación de PM2

```bash
npm install -g pm2
```

## Uso

### Iniciar el Backend con PM2 (Desarrollo)

```bash
cd Backend
pm2 start ecosystem.config.js
```

Para iniciar solo la aplicación Django:
```bash
pm2 start ecosystem.config.js --only control-bovino-backend
```

### Iniciar con Gunicorn (Producción)

```bash
pm2 start ecosystem.config.js --env production
```

### Ver estado de las aplicaciones

```bash
pm2 status
```

### Ver logs en tiempo real

```bash
pm2 logs control-bovino-backend
pm2 logs control-bovino-backend-gunicorn
```

### Detener todas las aplicaciones

```bash
pm2 stop all
```

### Reiniciar las aplicaciones

```bash
pm2 restart all
```

### Eliminar las aplicaciones de PM2

```bash
pm2 delete all
```

### Guardar la configuración de PM2

```bash
pm2 save
```

### Restaurar aplicaciones al iniciar el sistema (Linux/Mac)

```bash
pm2 startup
pm2 save
```

## Configuración del Archivo

**Development Mode (Django runserver)**
- Puerto: `0.0.0.0:8000`
- Watch: Monitorea cambios en `cardiaco_vaca/` y `temp_car/`
- Auto-restart: Sí
- Max Memory: 500MB

**Production Mode (Gunicorn)**
- Puerto: `0.0.0.0:8000`
- Workers: 4
- Timeout: 120s
- Max Memory: 1GB

## Notas Importantes

1. Asegúrate de tener instalados los requisitos:
   ```bash
   pip install -r requirements.txt
   ```

2. La base de datos debe estar migrada:
   ```bash
   python manage.py migrate
   ```

3. Los logs se guardan en `Backend/logs/`

4. El archivo está optimizado para ambientes locales (con rutas /Users/...). Para producción, actualiza las rutas según tu servidor.

## Troubleshooting

Si hay problemas de puerto en uso:
```bash
lsof -i :8000
kill -9 <PID>
```

Si PM2 no detecta cambios:
```bash
pm2 restart control-bovino-backend --watch
```

Para ver más detalles:
```bash
pm2 info control-bovino-backend
```
