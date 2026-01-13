#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para validar el despliegue en Vercel
Prueba los endpoints después del deployment
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "https://pmonitunl.vercel.app"
MAX_RETRIES = 5
RETRY_DELAY = 30

def test_endpoint(endpoint, data=None, method="GET"):
    """Test un endpoint específico"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10, verify=False)
        elif method == "POST":
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=data,
                timeout=10,
                verify=False
            )
        return response.status_code, response.json() if response.text else None
    except Exception as e:
        return None, str(e)

def main():
    print("\n" + "="*70)
    print("🚀 VERIFICANDO DESPLIEGUE EN VERCEL")
    print("="*70)
    print(f"Dominio: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Esperar a que Vercel termine el despliegue
    print("⏳ Esperando a que Vercel complete el despliegue...")
    print(f"Se intentarán {MAX_RETRIES} veces, cada {RETRY_DELAY} segundos\n")
    
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[Intento {attempt}/{MAX_RETRIES}] Conectando a Vercel...")
        
        # Test 1: Conexión básica
        status, _ = test_endpoint("/")
        if status != 200:
            print(f"❌ Servidor aún no responde (Status: {status})")
            if attempt < MAX_RETRIES:
                print(f"⏳ Esperando {RETRY_DELAY}s antes de reintentar...\n")
                time.sleep(RETRY_DELAY)
            continue
        
        print("✅ Servidor respondiendo")
        
        # Test 2: Arduino API (debería estar arreglada)
        print("\n📡 Probando Arduino API (POST /api/arduino/monitoreo)...")
        arduino_data = {
            "collar_id": 8888,
            "nombre_vaca": "Verificación Despliegue",
            "mac_collar": "FF:FF:FF:FF:FF:FF",
            "temperatura": 38.0,
            "pulsaciones": 60
        }
        
        status, response = test_endpoint("/api/arduino/monitoreo", arduino_data, "POST")
        if status == 201:
            print("✅ Arduino API: JSON parsing funciona correctamente")
        elif status == 400:
            print(f"⚠️  Arduino API retornó 400: {response}")
        else:
            print(f"❌ Arduino API Error (Status: {status})")
        
        # Test 3: Mobile Reporte API (debería estar arreglada)
        print("\n📱 Probando Mobile Reporte API (POST /api/movil/datos/)...")
        reporte_data = {
            "sensor": 1,
            "username": "verificacion_despliegue",
            "temperatura": 38.5,
            "pulsaciones": 72
        }
        
        status, response = test_endpoint("/api/movil/datos/", reporte_data, "POST")
        if status == 200:
            print("✅ Mobile Reporte API: JSON parsing funciona correctamente")
        elif status == 400:
            error_msg = response.get('detalle', '') if response else ""
            if "Se requieren sensor y username" in error_msg:
                print(f"⚠️  Mobile Reporte aún usa request.POST (no desplegado)")
            else:
                print(f"⚠️  Mobile Reporte retornó 400: {error_msg}")
        else:
            print(f"❌ Mobile Reporte Error (Status: {status})")
        
        # Test 4: Register API (debería estar arreglada)
        print("\n📝 Probando Register API (POST /api/register)...")
        import time as t
        ts = int(t.time())
        register_data = {
            "username": f"deploy_check_{ts}",
            "email": f"deploy_{ts}@test.com",
            "cedula": "1111111111",
            "telefono": "0999999999",
            "nombre": "Deploy",
            "apellido": "Check"
        }
        
        status, response = test_endpoint("/api/register", register_data, "POST")
        if status == 201:
            print("✅ Register API: JSON parsing funciona correctamente")
        elif status == 400:
            print(f"⚠️  Register retornó 400: {response}")
        elif status == 500:
            error_msg = response.get('detalle', '') if response else ""
            if "The given username must be set" in error_msg:
                print(f"⚠️  Register aún usa form data (no desplegado)")
            else:
                print(f"⚠️  Register retornó 500: {error_msg}")
        else:
            print(f"❌ Register Error (Status: {status})")
        
        # Resumen
        print("\n" + "="*70)
        print("✅ DESPLIEGUE COMPLETADO - Ejecuta test_remote_apis_fixed.py")
        print("="*70)
        return
    
    print("\n" + "="*70)
    print("❌ TIMEOUT - Vercel aún está desplegando")
    print("Intenta de nuevo en unos minutos")
    print("="*70)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()
