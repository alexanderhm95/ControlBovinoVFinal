#!/usr/bin/env bash
# Script de despliegue automatizado para ControlBovinoVFinal
# - Copia unit/systemd y conf nginx
# - Recarga systemd, habilita/inicia servicio gunicorn
# - Activa sitio nginx y reinicia
# - Configura UFW para la IP/puerto pedidos
# - Ejecuta migrate y collectstatic como usuario de despliegue
# Uso: sudo ./deploy.sh  (se requiere sudo)

set -euo pipefail

# Detectar la ubicación del script y establecer DEPLOY_DIR al padre (permite ejecutar desde /home/administrador)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# Puedes exportar DEPLOY_DIR antes de ejecutar el script para anularlo
DEPLOY_DIR="${DEPLOY_DIR:-$DEFAULT_DEPLOY_DIR}"

# Configuración (ajusta si tu instalación difiere)
SERVICE_FILE_SRC="$DEPLOY_DIR/deploy/gunicorn-controlbovino.service"
NGINX_CONF_SRC="$DEPLOY_DIR/deploy/nginx-controlbovino.conf"
ENV_FILE="$DEPLOY_DIR/deploy/.env"
SERVICE_NAME="gunicorn-controlbovino"
NGINX_SITE_NAME="controlbovino"
WWW_USER="www-data"
IP="190.96.102.30"
PORT="8081"
VENV_BIN="$DEPLOY_DIR/venv/bin"
MANAGE_PY="$DEPLOY_DIR/manage.py"

echo "Usando DEPLOY_DIR=$DEPLOY_DIR (si quieres otra ruta exporta DEPLOY_DIR antes de ejecutar)"

function die() {
  echo "ERROR: $*" >&2
  exit 1
}

if [ "$EUID" -ne 0 ]; then
  die "Este script debe ejecutarse con sudo/como root. Usa: sudo $0"
fi

[ -d "$DEPLOY_DIR" ] || die "No existe el directorio de despliegue: $DEPLOY_DIR"
[ -f "$SERVICE_FILE_SRC" ] || die "No se encontró $SERVICE_FILE_SRC"
[ -f "$NGINX_CONF_SRC" ] || die "No se encontró $NGINX_CONF_SRC"

echo "==> Copiando unit systemd: $SERVICE_FILE_SRC -> /etc/systemd/system/"
cp -f "$SERVICE_FILE_SRC" "/etc/systemd/system/$SERVICE_NAME.service"

echo "==> Recargando systemd y habilitando servicio"
systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
systemctl status --no-pager --full "$SERVICE_NAME" || true

echo "==> Instalando configuración Nginx"
NGINX_DEST="/etc/nginx/sites-available/$NGINX_SITE_NAME"
cp -f "$NGINX_CONF_SRC" "$NGINX_DEST"
ln -sfn "$NGINX_DEST" "/etc/nginx/sites-enabled/$NGINX_SITE_NAME"

echo "==> Comprobando configuración Nginx"
nginx -t
echo "==> Reiniciando Nginx"
systemctl restart nginx
systemctl status --no-pager --full nginx || true

echo "==> Configurando UFW (permitir acceso a $IP:$PORT)"
if command -v ufw >/dev/null 2>&1; then
  ufw allow from any to $IP port $PORT proto tcp || true
  ufw reload || true
  ufw status | grep "$PORT" || true
else
  echo "Aviso: ufw no está instalado. Omite configuración de firewall."
fi

echo "==> Ejecutando migraciones y collectstatic como $WWW_USER (puede tardar)"
if [ -x "$VENV_BIN/python" ]; then
  sudo -u "$WWW_USER" -H bash -lc "cd $DEPLOY_DIR && $VENV_BIN/python $MANAGE_PY migrate --noinput"
  sudo -u "$WWW_USER" -H bash -lc "cd $DEPLOY_DIR && $VENV_BIN/python $MANAGE_PY collectstatic --noinput"
else
  echo "Aviso: no se encontró Python en $VENV_BIN. Omitiendo migrate/collectstatic."
fi

echo "==> Estado de servicio gunicorn y últimos logs"
systemctl is-active --quiet "$SERVICE_NAME" && echo "Service $SERVICE_NAME está activo" || echo "Service $SERVICE_NAME no está activo"

echo "==> Últimas 200 líneas del journal del servicio"
journalctl -u "$SERVICE_NAME" -n 200 --no-pager || true

echo "==> Últimas 200 líneas del log de error de Nginx (si existe)"
if [ -f "/var/log/nginx/$NGINX_SITE_NAME.error.log" ]; then
  tail -n 200 "/var/log/nginx/$NGINX_SITE_NAME.error.log"
else
  tail -n 200 /var/log/nginx/error.log 2>/dev/null || true
fi

echo "==> Comprobación HTTP rápida (curl)"
if command -v curl >/dev/null 2>&1; then
  echo "Probando http://$IP:$PORT/ ..."
  curl -I --max-time 5 "http://$IP:$PORT/" || echo "curl falló o sin respuesta"
else
  echo "curl no instalado, omitiendo prueba HTTP."
fi

echo "Despliegue finalizado. Revisa los logs si hay problemas."
 
# Make the script executable if running from the repo location
if [ "$(id -u)" -eq 0 ]; then
  chmod +x "$SCRIPT_DIR/deploy.sh" 2>/dev/null || true
fi
