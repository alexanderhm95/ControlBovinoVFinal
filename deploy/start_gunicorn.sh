#!/usr/bin/env bash
# Script auxiliar para arrancar gunicorn manualmente desde el venv (útil para debugging)
# Ajustar dinámicamente la ruta base al padre del script (funciona desde /home/administrador o /home/www-data)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="$BASE_DIR/venv"
cd "$BASE_DIR"
# Cargar variables de entorno si existen
if [ -f "$BASE_DIR/deploy/.env" ]; then
  export $(grep -v '^#' "$BASE_DIR/deploy/.env" | xargs)
fi
# Crear directorio runtime para el socket si no existe (útil para arranques manuales)
RUNDIR="/run/gunicorn-controlbovino"
if [ ! -d "$RUNDIR" ]; then
  mkdir -p "$RUNDIR"
  # Intentar asignar ownership al usuario actual (si falla, no abortar)
  chown "${USER:-$(whoami)}:${USER:-$(whoami)}" "$RUNDIR" 2>/dev/null || true
fi
# Activar venv
source "$VENV/bin/activate"
# Ejecutar gunicorn (socket dentro del RuntimeDirectory creado por systemd)
exec gunicorn --access-logfile - --error-logfile - --workers 3 --bind unix:/run/gunicorn-controlbovino/gunicorn-controlbovino.sock cardiaco_vaca.wsgi:application
