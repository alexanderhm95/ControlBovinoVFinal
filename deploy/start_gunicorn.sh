#!/usr/bin/env bash
# Script auxiliar para arrancar gunicorn manualmente desde el venv (útil para debugging)
set -euo pipefail
BASE_DIR="/home/www-data/ControlBovinoVFinal"
VENV="$BASE_DIR/venv"
cd "$BASE_DIR"
# Cargar variables de entorno si existen
if [ -f "$BASE_DIR/deploy/.env" ]; then
  export $(grep -v '^#' "$BASE_DIR/deploy/.env" | xargs)
fi
# Activar venv
source "$VENV/bin/activate"
# Ejecutar gunicorn
exec gunicorn --access-logfile - --error-logfile - --workers 3 --bind unix:/run/gunicorn-controlbovino.sock cardiaco_vaca.wsgi:application
