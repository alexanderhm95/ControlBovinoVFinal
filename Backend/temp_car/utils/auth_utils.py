"""
Utilidades de autenticación para APIs
Soporta autenticación por API Key para dispositivos Arduino
"""

from functools import wraps
from django.http import JsonResponse
from django.conf import settings

# Clave API configurada en settings o variable de entorno
ARDUINO_API_KEY = getattr(settings, 'ARDUINO_API_KEY', 'sk_test_controlbovino_2024')

def require_api_key(view_func):
    """
    Decorador para validar API Key en requests de Arduino
    Espera header: Authorization: Bearer YOUR_API_KEY
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Obtener header de autorización
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return JsonResponse({
                'error': 'No autorizado',
                'detalle': 'Se requiere header Authorization'
            }, status=401)
        
        # Validar formato "Bearer TOKEN"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return JsonResponse({
                'error': 'No autorizado',
                'detalle': 'Formato inválido: Bearer TOKEN'
            }, status=401)
        
        api_key = parts[1]
        
        # Validar clave
        if api_key != ARDUINO_API_KEY:
            print(f"[AUTH] ❌ API Key inválida: {api_key[:10]}...")
            return JsonResponse({
                'error': 'No autorizado',
                'detalle': 'API Key inválida'
            }, status=401)
        
        print(f"[AUTH] ✅ API Key válida")
        return view_func(request, *args, **kwargs)
    
    return wrapper


def get_api_key_from_request(request):
    """
    Extrae la API Key del header Authorization
    Retorna None si no existe o es inválida
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) == 2 and parts[0] == 'Bearer':
        return parts[1]
    
    return None
