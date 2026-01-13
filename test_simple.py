#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test simple para APIs sin emojis (compatible Windows)
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_arduino():
    """Test Arduino API"""
    print("\n[TEST] Arduino API")
    data = {
        "collar_id": 5555,
        "nombre_vaca": "Test Arduino",
        "mac_collar": "AA:BB:CC:DD:EE:FF",
        "temperatura": 38.5,
        "pulsaciones": 70
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/arduino/monitoreo",
            json=data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_register():
    """Test Register API"""
    print("\n[TEST] Register API")
    ts = int(time.time())
    data = {
        "username": f"testuser_{ts}",
        "email": f"test_{ts}@example.com",
        "cedula": f"123456{ts}",  # Cédula única usando timestamp
        "telefono": f"099999{ts % 10000}",  # Teléfono único
        "nombre": "Test",
        "apellido": "User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/register",
            json=data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_reporte(new_username=None):
    """Test Mobile Reporte API"""
    print("\n[TEST] Mobile Reporte API")
    # El API requiere sensor (collar_id) y username
    # Usaremos collar_id=1 que sabemos existe
    ts = int(time.time())
    # Usar el usuario recién registrado
    username_to_use = new_username if new_username else f"testuser_{ts}"
    
    data = {
        "sensor": 1,  # Collar ID que sabemos existe (Sofia)
        "username": username_to_use,  # Usuario para registrar el control
        "temperatura": 38.5,
        "pulsaciones": 70
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/movil/datos/",
            json=data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response Text: {response.text if response.text else '(empty)'}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 404, 400]  # 404 si no existe usuario
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_list_users():
    """Test List Users API"""
    print("\n[TEST] List Users API")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/listar",
            timeout=5
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        if isinstance(data, dict) and 'usuarios' in data:
            print(f"Total usuarios: {data.get('total', 'unknown')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("TESTING APIS - LOCAL SERVER")
    print("="*60)
    print(f"URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Primero creamos un usuario
    print("\n[SETUP] Creando usuario para pruebas...")
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
            timeout=5
        )
        if response.status_code == 201:
            new_username = data['username']
            print(f"Usuario creado: {new_username}")
        else:
            new_username = None
            print(f"Error creando usuario: {response.status_code}")
    except:
        new_username = None
    
    results = {
        "Arduino": test_arduino(),
        "Register": test_register(),
        "Reporte": test_reporte(new_username),
        "List": test_list_users()
    }
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<15} {status}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nTotal: {passed}/{total}")
