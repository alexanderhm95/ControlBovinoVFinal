#!/bin/bash
cd /home/administrador/ControlBovinoVFinal/Backend
/home/administrador/ControlBovinoVFinal/venv/bin/gunicorn cardiaco_vaca.wsgi:application \
    --workers 4 \
    --threads 2 \
    --bind 0.0.0.0:8081 \
    --timeout 120
