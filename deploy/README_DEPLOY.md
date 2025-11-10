Guía de despliegue en Ubuntu (IP 190.96.102.30, puerto 8081)

Resumen: esta guía asume que desplegarás la app en /home/www-data/ControlBovinoVFinal con un virtualenv en /home/www-data/ControlBovinoVFinal/venv. Nginx escuchará en 190.96.102.30:8081 y hará proxy al socket de gunicorn.

Pasos (comandos a ejecutar en el servidor Ubuntu):

1) Crear usuario de despliegue (opcional)

sudo adduser --disabled-password --gecos "" www-data
sudo usermod -aG www-data $USER   # (opcional) añadir tu usuario para acceso

2) Actualizar sistema e instalar dependencias

sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip build-essential git nginx \
    libpq-dev postgresql-client ufw

3) Clonar repo y preparar venv

# suponiendo que usas /home/www-data
sudo -u www-data -H bash -lc 'git clone <REPO_URL> /home/www-data/ControlBovinoVFinal'
cd /home/www-data/ControlBovinoVFinal
sudo -u www-data -H bash -lc 'python3 -m venv venv'
sudo -u www-data -H bash -lc '/home/www-data/ControlBovinoVFinal/venv/bin/pip install --upgrade pip'
sudo -u www-data -H bash -lc '/home/www-data/ControlBovinoVFinal/venv/bin/pip install -r requirements.txt'

4) Configurar variables de entorno

cp deploy/.env.example deploy/.env
# Edita deploy/.env y pon SECRET_KEY, DEBUG=False, ALLOWED_HOSTS (incluye IP o dominio)

5) Migraciones y collectstatic

sudo -u www-data -H bash -lc '/home/www-data/ControlBovinoVFinal/venv/bin/python manage.py migrate --noinput'
sudo -u www-data -H bash -lc '/home/www-data/ControlBovinoVFinal/venv/bin/python manage.py collectstatic --noinput'

6) Configurar systemd para gunicorn

# Copia deploy/gunicorn-controlbovino.service a /etc/systemd/system/
sudo cp deploy/gunicorn-controlbovino.service /etc/systemd/system/gunicorn-controlbovino.service
# Edita el archivo si cambias rutas/usuario
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-controlbovino
sudo systemctl status gunicorn-controlbovino

7) Configurar Nginx

# Copia el archivo y actívalo
sudo cp deploy/nginx-controlbovino.conf /etc/nginx/sites-available/controlbovino
sudo ln -s /etc/nginx/sites-available/controlbovino /etc/nginx/sites-enabled/
# Asegúrate de que proxy_params está disponible (viene con nginx)
sudo nginx -t
sudo systemctl restart nginx

8) Firewall

# Permitir tráfico TCP al puerto 8081 en la IP pública indicada
sudo ufw allow from any to 190.96.102.30 port 8081 proto tcp
sudo ufw enable
sudo ufw status

9) Verificación

# Revisar logs
sudo journalctl -u gunicorn-controlbovino -f
sudo tail -n 200 /var/log/nginx/controlbovino.error.log

10) Notas y recomendaciones

- Para seguridad, usa PostgreSQL en vez de SQLite en producción. Están listadas dependencias en requirements.txt (psycopg2-binary).
- Considera obtener certificados TLS (Let's Encrypt) y usar Nginx en 443; para portar 8081 detrás de TLS puedes usar port 443 y proxy pasar igual.
- Asegúrate de poner DEBUG=False y un SECRET_KEY robusto en deploy/.env.
- Revisa permisos de /home/www-data/ControlBovinoVFinal/staticfiles y media.

Nota sobre socket y systemd
--------------------------------
En la configuración actual el servicio systemd crea un RuntimeDirectory llamado `gunicorn-controlbovino` en `/run/` y el socket de Gunicorn se encuentra en:

    /run/gunicorn-controlbovino/gunicorn-controlbovino.sock

Esto evita problemas de permisos al crear el socket desde systemd y mantiene los artefactos en runtime. Si arrancas Gunicorn manualmente con `deploy/start_gunicorn.sh`, el script ya está adaptado para usar esta ruta de socket.

Si quieres, puedo generar los comandos exactos adaptados a tu servidor (usuario, dominio o IP) y opcionalmente preparar el archivo de systemd listo para copiar al servidor.
