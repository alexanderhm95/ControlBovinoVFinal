"""
Settings para migración a PostgreSQL local
"""
from .settings import *
import dj_database_url

# Configuración de PostgreSQL local
# Instala PostgreSQL y crea una base de datos llamada 'controlbovino_local'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'controlbovino_local',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',  # Cambia por tu password de PostgreSQL
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# O usando DATABASE_URL si prefieres
# DATABASE_URL = 'postgresql://postgres:tu_password@localhost:5432/controlbovino_local'
# DATABASES = {
#     'default': dj_database_url.parse(DATABASE_URL)
# }

DEBUG = True