#!/usr/bin/env python3
"""
Test script para probar todas las APIs en Vercel después del despliegue.
Valida que los fixes de JSON handling funcionan en producción.
"""

import requests
import json
import time
from datetime import datetime

# Dominio remoto de Vercel
BASE_URL = "https://pmonitunl.vercel.app"
TIMEOUT = 10

def test_register():
    """Test Register API - POST /api/register"""
    print("\n[TEST] Register API (Remote)")
    ts = int(time.time())
    data = {
        "username": f"testuser_{ts}",
        "email": f"test_{ts}@example.com",
        "cedula": f"123456{ts}",
        "telefono": f"099999{ts % 10000}",
        "nombre": "Test",
        "apellido": "User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/register",
            json=data,
            timeout=TIMEOUT
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✓ PASS - Usuario creado: {result.get('data', {}).get('username')}")
            return result.get('data', {}).get('username'), "PASS"
        else:
            print(f"✗ FAIL - {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None, "FAIL"
    except Exception as e:
        print(f"✗ ERROR - {str(e)}")
        return None, "ERROR"

def test_arduino():
    """Test Arduino API - POST /api/arduino/monitoreo"""
    print("\n[TEST] Arduino API (Remote)")
    ts = int(time.time())
    data = {
        "collar_id": 5555 + (ts % 1000),
        "nombre_vaca": "Test Arduino",
        "mac_collar": f"AA:BB:CC:DD:EE:{ts % 100:02d}",
        "temperatura": 38.5,
        "pulsaciones": 70
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/arduino/monitoreo",
            json=data,
            timeout=TIMEOUT
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✓ PASS - Lectura registrada")
            return "PASS"
        else:
            print(f"✗ FAIL - {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return "FAIL"
    except Exception as e:
        print(f"✗ ERROR - {str(e)}")
        return "ERROR"

def test_reporte(username):
    """Test Mobile Reporte API - POST /api/movil/datos/"""
    print("\n[TEST] Mobile Reporte API (Remote)")
    
    if not username:
        username = "admin"  # Usuario por defecto
    
    data = {
        "sensor": 1,  # Collar que sabemos existe
        "username": username
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/movil/datos/",
            json=data,
            timeout=TIMEOUT
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ PASS - Reporte obtenido")
            return "PASS"
        else:
            print(f"✗ FAIL - {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return "FAIL"
    except Exception as e:
        print(f"✗ ERROR - {str(e)}")
        return "ERROR"

def test_list():
    """Test List API - GET /api/listar"""
    print("\n[TEST] List Users API (Remote)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/listar",
            timeout=TIMEOUT
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            count = len(result.get('usuarios', []))
            print(f"✓ PASS - {count} usuarios encontrados")
            return "PASS"
        else:
            print(f"✗ FAIL - {response.status_code}")
            return "FAIL"
    except Exception as e:
        print(f"✗ ERROR - {str(e)}")
        return "ERROR"

if __name__ == "__main__":
    print("="*70)
    print("TESTING APIS - REMOTE VERCEL SERVER")
    print("="*70)
    print(f"URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Timeout: {TIMEOUT}s")
    
    results = {}
    
    # Test 1: Register (crea un usuario que usaremos después)
    new_username, results['Register'] = test_register()
    
    # Test 2: Arduino
    results['Arduino'] = test_arduino()
    
    # Test 3: Reporte (usa el usuario creado)
    results['Reporte'] = test_reporte(new_username)
    
    # Test 4: List
    results['List'] = test_list()
    
    # Resumen
    print("\n" + "="*70)
    print("RESULTADOS")
    print("="*70)
    passed = sum(1 for v in results.values() if v == "PASS")
    total = len(results)
    
    for api, status in results.items():
        symbol = "✓" if status == "PASS" else "✗"
        print(f"{symbol} {api:20} {status}")
    
    print(f"\nTotal: {passed}/{total} ({100*passed//total}%)")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS APIS FUNCIONAN EN VERCEL!")
    else:
        print(f"\n⚠️  {total-passed} API(s) fallando en Vercel")
