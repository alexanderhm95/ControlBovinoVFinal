#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test directo en Django shell sin necesidad de requests
"""

import os
import django
import json
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cardiaco_vaca.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

client = Client()

def test_arduino():
    """Test Arduino API"""
    print("\n[TEST] Arduino API - POST /api/arduino/monitoreo")
    data = {
        "collar_id": 5555,
        "nombre_vaca": "Test Arduino",
        "mac_collar": "AA:BB:CC:DD:EE:FF",
        "temperatura": 38.5,
        "pulsaciones": 70
    }
    
    try:
        response = client.post(
            "/api/arduino/monitoreo",
            json.dumps(data),
            content_type="application/json"
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_register():
    """Test Register API"""
    print("\n[TEST] Register API - POST /api/register")
    ts = int(time.time())
    data = {
        "username": f"testuser_{ts}",
        "email": f"test_{ts}@example.com",
        "cedula": "1234567890",
        "telefono": "0999999999",
        "nombre": "Test",
        "apellido": "User"
    }
    
    try:
        response = client.post(
            "/api/register",
            json.dumps(data),
            content_type="application/json"
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_reporte():
    """Test Mobile Reporte API"""
    print("\n[TEST] Mobile Reporte API - POST /api/movil/datos/")
    data = {
        "sensor": 1,
        "username": "test",
        "temperatura": 38.5,
        "pulsaciones": 70
    }
    
    try:
        response = client.post(
            "/api/movil/datos/",
            json.dumps(data),
            content_type="application/json"
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        # Esperamos 200, 404 (usuario no existe) o 400 (error de validacion)
        return response.status_code in [200, 404, 400]
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_list_users():
    """Test List Users API"""
    print("\n[TEST] List Users API - GET /api/listar")
    
    try:
        response = client.get("/api/listar")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("TESTING APIS - DJANGO TEST CLIENT")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Arduino": test_arduino(),
        "Register": test_register(),
        "Reporte": test_reporte(),
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
