"""
Settings para migración a PostgreSQL local
"""
from .settings import *
import dj_database_url


# Configuración dinámica: usa DATABASE_URL si está presente, si no usa config local
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:tu_password@localhost:5432/controlbovino_local'
    )
}

DEBUG = True