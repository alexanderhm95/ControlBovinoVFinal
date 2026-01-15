#!/usr/bin/env python3
"""
Script para preparar la aplicación para desplegarse en Render.com
Genera la configuración necesaria para que Render ejecute migraciones automáticamente.
"""

import os

# Crear build.sh para que Render ejecute migraciones
build_script = """#!/bin/bash
set -o errexit

pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --no-input
"""

with open('build.sh', 'w') as f:
    f.write(build_script)

os.chmod('build.sh', 0o755)

print("✅ Creado: build.sh")
print("\nPasos para desplegar en Render:")
print("1. Ir a https://render.com")
print("2. Conectar GitHub")
print("3. Crear nuevo 'Web Service'")
print("4. Seleccionar repositorio ControlBovinoVFinal")
print("5. Configurar:")
print("   - Name: controlbovino")
print("   - Environment: Python 3")
print("   - Build Command: ./build.sh")
print("   - Start Command: gunicorn cardiaco_vaca.wsgi")
print("6. Agregar variable de entorno:")
print("   - Name: PYTHON_VERSION")
print("   - Value: 3.11.4")
