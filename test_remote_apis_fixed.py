#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar APIs Arduino y Mobile contra el dominio remoto
URL Base: https://pmonitunl.vercel.app/
Con los campos correctos según las vistas actuales
"""

import requests
import json
from datetime import datetime
import time
import urllib3

# Desactivar warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración
BASE_URL = "https://pmonitunl.vercel.app"
TIMEOUT = 10

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def test_api_connection():
    """Prueba conexión básica al servidor"""
    print_header("TEST 1: CONEXIÓN AL SERVIDOR REMOTO")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT, verify=False)
        print_info(f"URL: {BASE_URL}")
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code < 500:
            print_success("Servidor remoto accesible ✓")
            return True
        else:
            print_error("Servidor respondió con error")
            return False
    except Exception as e:
        print_error(f"No se puede conectar: {str(e)}")
        return False

def test_list_users():
    """Prueba List Users API - DEBE FUNCIONAR"""
    print_header("TEST 2: LIST USERS API (GET /api/listar)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/listar",
            timeout=TIMEOUT,
            verify=False
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            
            if isinstance(data, dict) and 'usuarios' in data:
                usuarios = data['usuarios']
                print_info(f"Total usuarios encontrados: {len(usuarios)}")
                
                if usuarios:
                    first_user_id = list(usuarios.keys())[0]
                    first_user = usuarios[first_user_id]
                    print_info(f"Ejemplo usuario:")
                    print_info(f"  - ID: {first_user.get('userId')}")
                    print_info(f"  - Email: {first_user.get('email')}")
                    print_info(f"  - Nombre: {first_user.get('nombre_completo')}")
                    
                    # Guardar para login
                    return True, first_user.get('email'), usuarios
            
            if response.status_code == 200:
                print_success("List Users API funcionando ✓")
                return True, None, data
            else:
                print_warning(f"Status inesperado: {response.status_code}")
                return False, None, None
        except:
            print_info(f"Response: {response.text}")
            return False, None, None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False, None, None

def test_mobile_login(email):
    """Prueba Login API para Mobile con email real"""
    print_header("TEST 3: MOBILE LOGIN API (POST /api/movil/login/)")
    
    if not email:
        print_warning("No hay usuario disponible para login")
        return False
    
    try:
        # Probar con diferentes combinaciones
        credentials_list = [
            {"username": email, "password": "test123"},
            {"username": email.split('@')[0], "password": "test123"},
            {"email": email, "password": "test123"}
        ]
        
        for creds in credentials_list:
            print_info(f"Intentando con: {json.dumps(creds)}")
            
            response = requests.post(
                f"{BASE_URL}/api/movil/login/",
                json=creds,
                timeout=TIMEOUT,
                verify=False
            )
            
            print_info(f"Status Code: {response.status_code}")
            
            try:
                data = response.json()
                print_info(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status_code == 200:
                    print_success("Login API funcionando ✓")
                    return True
                elif response.status_code == 401:
                    print_warning(f"Credenciales inválidas (contraseña probablemente diferente)")
                else:
                    print_info(f"Status {response.status_code} - continuando...")
            except:
                pass
        
        print_warning("Login requiere contraseña válida del usuario (no disponible en test)")
        return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_arduino_data_fixed():
    """Prueba Arduino Data API con los campos CORRECTOS"""
    print_header("TEST 4: ARDUINO DATA API (POST /api/arduino/monitoreo)")
    print_info("Campos requeridos: collar_id (int), nombre_vaca, mac_collar, temperatura")
    
    try:
        # Datos con los campos correctos - collar_id DEBE SER NÚMERO ENTERO
        arduino_data = {
            "collar_id": 999,  # ✅ Número entero, no string
            "nombre_vaca": "Vaca Prueba Arduino",
            "mac_collar": "AA:BB:CC:DD:EE:FF",
            "temperatura": 38.5,
            "pulsaciones": 72
        }
        
        print_info(f"Enviando datos Arduino:\n{json.dumps(arduino_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/arduino/monitoreo",
            json=arduino_data,
            timeout=TIMEOUT,
            verify=False
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print_info(f"Response:\n{json.dumps(data, indent=2)}")
            
            if response.status_code in [200, 201]:
                print_success("Arduino API funcionando ✓")
                return True
            elif response.status_code == 400:
                print_warning(f"Validación fallida - verifica campos")
                return False
            else:
                print_warning(f"Status: {response.status_code}")
                return False
        except:
            print_info(f"Response Text: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_mobile_reporte_fixed():
    """Prueba Mobile Reporte API con campos CORRECTOS"""
    print_header("TEST 5: MOBILE REPORTE API (POST /api/movil/datos/)")
    print_info("Campos requeridos: sensor (int, collar_id), username")
    
    try:
        reporte_data = {
            "sensor": 1,  # ✅ Número entero (collar_id existente)
            "username": "test_user",
            "temperatura": 38.5,
            "pulsaciones": 72,
            "observaciones": "Prueba desde Vercel"
        }
        
        print_info(f"Enviando reporte:\n{json.dumps(reporte_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/movil/datos/",
            json=reporte_data,
            timeout=TIMEOUT,
            verify=False
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print_info(f"Response:\n{json.dumps(data, indent=2)}")
            
            if response.status_code in [200, 201]:
                print_success("Reporte API funcionando ✓")
                return True
            elif response.status_code == 400:
                print_warning("Validación fallida - verifica campos")
                return False
            else:
                print_warning(f"Status: {response.status_code}")
                return False
        except:
            print_info(f"Response Text: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_api_register_fixed():
    """Prueba Register API - VERSIÓN CORRECTA"""
    print_header("TEST 6: USER REGISTER API (POST /api/register)")
    print_info("Revisando validación del formulario...")
    
    try:
        timestamp = int(time.time())
        register_data = {
            "username": f"testuser{timestamp}",
            "email": f"test{timestamp}@example.com",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
            "cedula": "1234567890",
            "telefono": "0999999999",
            "nombre": "Test",
            "apellido": "Usuario"
        }
        
        print_info(f"Registrando usuario:\n{json.dumps(register_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/register",
            json=register_data,
            timeout=TIMEOUT,
            verify=False
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print_info(f"Response:\n{json.dumps(data, indent=2)}")
            
            if response.status_code in [200, 201]:
                print_success("Register API funcionando ✓")
                return True
            else:
                print_warning(f"Status: {response.status_code} - El endpoint puede estar deshabilitado")
                return False
        except:
            print_info(f"Response Text: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_dashboard_data():
    """Prueba Dashboard Data API"""
    print_header("TEST 7: DASHBOARD DATA API (GET /monitor/datos/<id>/)")
    print_info("Intentando con ID = 1")
    
    try:
        response = requests.get(
            f"{BASE_URL}/monitor/datos/1/",
            timeout=TIMEOUT,
            verify=False
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        try:
            if response.text:
                data = response.json()
                print_info(f"Response (primeros 500 chars):\n{json.dumps(data, indent=2)[:500]}")
                
                if response.status_code == 200:
                    print_success("Dashboard Data API funcionando ✓")
                    return True
                else:
                    print_warning(f"Status: {response.status_code}")
                    return False
            else:
                print_warning("Respuesta vacía")
                return False
        except:
            print_info(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_cors_detailed():
    """Prueba CORS de manera más detallada"""
    print_header("TEST 8: CORS CONFIGURATION")
    
    try:
        # Probar con un OPTIONS request a diferentes endpoints
        endpoints = [
            "/api/arduino/monitoreo",
            "/api/movil/login/",
            "/api/listar"
        ]
        
        cors_working = False
        for endpoint in endpoints:
            print_info(f"Probando CORS en: {endpoint}")
            
            try:
                response = requests.options(
                    f"{BASE_URL}{endpoint}",
                    timeout=TIMEOUT,
                    verify=False,
                    headers={"Origin": "https://example.com"}
                )
                
                cors_header = response.headers.get('Access-Control-Allow-Origin')
                if cors_header:
                    print_success(f"CORS permitido para: {cors_header}")
                    cors_working = True
                else:
                    print_warning(f"No hay CORS header en {endpoint}")
            except:
                pass
        
        if cors_working:
            print_success("CORS está configurado ✓")
            return True
        else:
            print_warning("CORS puede no estar completamente configurado")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas mejoradas"""
    print_header("🚀 PRUEBAS DE API REMOTA - CONTROL BOVINO (VERSIÓN MEJORADA)")
    print_info(f"Dominio: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Conexión": False,
        "List Users": False,
        "Mobile Login": False,
        "Arduino Data": False,
        "Mobile Reporte": False,
        "Register": False,
        "Dashboard Data": False,
        "CORS": False
    }
    
    # Test 1: Conexión
    results["Conexión"] = test_api_connection()
    if not results["Conexión"]:
        print_error("\n⚠️  El servidor no está accesible. Abortando pruebas...")
        return results
    
    time.sleep(0.5)
    
    # Test 2: List Users (para obtener usuario real)
    success, email, usuarios = test_list_users()
    results["List Users"] = success
    time.sleep(0.5)
    
    # Test 3: Mobile Login
    success = test_mobile_login(email)
    results["Mobile Login"] = success
    time.sleep(0.5)
    
    # Test 4: Arduino Data (con campos correctos)
    results["Arduino Data"] = test_arduino_data_fixed()
    time.sleep(0.5)
    
    # Test 5: Mobile Reporte (con campos correctos)
    results["Mobile Reporte"] = test_mobile_reporte_fixed()
    time.sleep(0.5)
    
    # Test 6: Register
    results["Register"] = test_api_register_fixed()
    time.sleep(0.5)
    
    # Test 7: Dashboard Data
    results["Dashboard Data"] = test_dashboard_data()
    time.sleep(0.5)
    
    # Test 8: CORS
    results["CORS"] = test_cors_detailed()
    
    # Resumen Final
    print_header("📊 RESUMEN DE PRUEBAS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{test_name:<20} {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} pruebas pasadas ({(passed/total)*100:.0f}%){Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡TODAS LAS PRUEBAS PASARON!{Colors.END}")
    elif passed >= total * 0.6:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  {total - passed} pruebas fallaron{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Múltiples fallos detectados{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}RECOMENDACIONES:{Colors.END}")
    print(f"1. Los campos Arduino deben incluir 'nombre_vaca'")
    print(f"2. Los campos Mobile Reporte deben usar 'sensor' en lugar de 'collar_id'")
    print(f"3. Verificar que el Register endpoint esté habilitado en producción")
    print(f"4. Confirmar CORS en settings.py para Vercel")
    
    return results

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.END}")
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
