"""
Configuración de variables de entorno para APIs
Actualizar con valores reales en producción
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ==================== BASE ====================
# URL base del servidor
API_BASE_URL = os.getenv('API_BASE_URL', 'https://pmonitunl.vercel.app/api')

# ==================== ARDUINO ====================
# Clave API para Arduino
ARDUINO_API_KEY = os.getenv('ARDUINO_API_KEY', 'sk_arduino_controlbovino_2024')

# Timeout para peticiones (segundos)
ARDUINO_REQUEST_TIMEOUT = int(os.getenv('ARDUINO_REQUEST_TIMEOUT', '10'))

# ==================== FLUTTER ====================
# Habilitar HTTPS
FLUTTER_USE_HTTPS = os.getenv('FLUTTER_USE_HTTPS', 'true').lower() == 'true'

# Base URL para Flutter
FLUTTER_BASE_URL = os.getenv('FLUTTER_BASE_URL', API_BASE_URL)

# Timeout para peticiones (segundos)
FLUTTER_REQUEST_TIMEOUT = int(os.getenv('FLUTTER_REQUEST_TIMEOUT', '15'))

# ==================== JWT/TOKENS ====================
# Secreto para generar tokens
JWT_SECRET = os.getenv('JWT_SECRET', 'secret_key_change_in_production')

# Tiempo de expiración de token (minutos)
TOKEN_EXPIRY_MINUTES = int(os.getenv('TOKEN_EXPIRY_MINUTES', '60'))

# ==================== CORS ====================
# Dominios permitidos
CORS_ALLOWED_ORIGINS = [
    'https://pmonitunl.vercel.app',
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:8080',
]

# ==================== LOGGING ====================
# Nivel de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Archivo de log
LOG_FILE = os.getenv('LOG_FILE', 'logs/api.log')

# ==================== SENSORES ====================
# Rangos normales de valores
TEMP_MIN_NORMAL = float(os.getenv('TEMP_MIN_NORMAL', '38'))  # °C
TEMP_MAX_NORMAL = float(os.getenv('TEMP_MAX_NORMAL', '39'))  # °C

HR_MIN_NORMAL = int(os.getenv('HR_MIN_NORMAL', '60'))  # BPM
HR_MAX_NORMAL = int(os.getenv('HR_MAX_NORMAL', '80'))  # BPM

# Estados de salud
HEALTH_STATES = {
    'normal': 'Normal - Todos los valores dentro del rango',
    'alert': 'Alerta - Al menos un valor fuera del rango',
    'critical': 'Crítico - Múltiples valores fuera del rango',
    'unknown': 'Desconocido - Datos insuficientes'
}
