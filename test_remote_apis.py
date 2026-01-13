#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar APIs Arduino y Mobile contra el dominio remoto
URL Base: https://pmonitunl.vercel.app/
"""

import requests
import json
from datetime import datetime
import time

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
    """Imprime un encabezado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def test_api_connection():
    """Prueba conexión básica al servidor"""
    print_header("TEST 1: CONEXIÓN AL SERVIDOR REMOTO")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        print_info(f"URL: {BASE_URL}")
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code < 500:
            print_success("Servidor remoto accesible")
            return True
        else:
            print_error("Servidor respondió con error")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"No se puede conectar a {BASE_URL}")
        print_warning("Verifica que la URL sea correcta y esté en línea")
        return False
    except requests.exceptions.Timeout:
        print_error(f"Timeout al conectar a {BASE_URL}")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_mobile_login():
    """Prueba Login API para Mobile"""
    print_header("TEST 2: MOBILE LOGIN API")
    print_info("Endpoint: POST /api/movil/login/")
    
    try:
        credentials = {
            "username": "test_user",
            "password": "test_password"
        }
        
        print_info(f"Enviando credenciales: {json.dumps(credentials, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/movil/login/",
            json=credentials,
            timeout=TIMEOUT,
            verify=False  # Para desarrollo
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print_info(f"Response Body:\n{json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                print_success("Login API funcionando correctamente")
                return True, data
            elif response.status_code == 401:
                print_warning("Credenciales inválidas (esperado si el usuario no existe)")
                return False, data
            else:
                print_warning(f"Status inesperado: {response.status_code}")
                return False, data
        except:
            print_info(f"Response Text: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print_error("No se puede conectar al endpoint /api/movil/login/")
        return False, None
    except Exception as e:
        print_error(f"Error en login: {str(e)}")
        return False, None

def test_arduino_data():
    """Prueba Arduino Data API"""
    print_header("TEST 3: ARDUINO DATA API")
    print_info("Endpoint: POST /api/arduino/monitoreo")
    
    try:
        # Datos de ejemplo desde Arduino
        arduino_data = {
            "collar_id": "ABC123",
            "mac": "00:11:22:33:44:55",
            "temperatura": 38.5,
            "pulsaciones": 72,
            "timestamp": datetime.now().isoformat()
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
                print_success("Arduino API funcionando correctamente")
                return True, data
            else:
                print_warning(f"Status: {response.status_code}")
                return False, data
        except:
            print_info(f"Response Text: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print_error("No se puede conectar al endpoint /api/arduino/monitoreo")
        return False, None
    except Exception as e:
        print_error(f"Error en Arduino API: {str(e)}")
        return False, None

def test_mobile_reporte():
    """Prueba Mobile Reporte API"""
    print_header("TEST 4: MOBILE REPORTE API")
    print_info("Endpoint: POST /api/movil/datos/")
    
    try:
        reporte_data = {
            "collar_id": "ABC123",
            "temperatura": 38.5,
            "pulsaciones": 72,
            "user_id": 1,
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
                print_success("Reporte API funcionando")
                return True, data
            else:
                print_warning(f"Status: {response.status_code}")
                return False, data
        except:
            print_info(f"Response Text: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Error en Reporte API: {str(e)}")
        return False, None

def test_api_register():
    """Prueba Register API"""
    print_header("TEST 5: USER REGISTER API")
    print_info("Endpoint: POST /api/register")
    
    try:
        register_data = {
            "username": f"test_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
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
                print_success("Register API funcionando")
                return True, data
            else:
                print_warning(f"Status: {response.status_code}")
                return False, data
        except:
            print_info(f"Response Text: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Error en Register API: {str(e)}")
        return False, None

def test_api_listar():
    """Prueba List Users API"""
    print_header("TEST 6: LIST USERS API")
    print_info("Endpoint: GET /api/listar")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/listar",
            timeout=TIMEOUT,
            verify=False
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            
            if isinstance(data, list):
                print_info(f"Total usuarios: {len(data)}")
                if len(data) > 0:
                    print_info(f"Primer usuario (muestra):\n{json.dumps(data[0], indent=2, default=str)}")
            else:
                print_info(f"Response:\n{json.dumps(data, indent=2, default=str)}")
            
            if response.status_code == 200:
                print_success("List API funcionando")
                return True, data
            else:
                print_warning(f"Status: {response.status_code}")
                return False, data
        except:
            print_info(f"Response Text: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Error en List API: {str(e)}")
        return False, None

def test_cors_headers():
    """Prueba headers CORS"""
    print_header("TEST 7: CORS HEADERS")
    
    try:
        response = requests.options(
            f"{BASE_URL}/api/arduino/monitoreo",
            timeout=TIMEOUT,
            verify=False
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        print_info(f"CORS Headers:\n{json.dumps(cors_headers, indent=2)}")
        
        if cors_headers['Access-Control-Allow-Origin']:
            print_success("CORS configurado correctamente")
            return True
        else:
            print_warning("CORS headers no detectados")
            return False
            
    except Exception as e:
        print_warning(f"No se pudo probar CORS: {str(e)}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print_header("🚀 PRUEBAS DE API REMOTA - CONTROL BOVINO")
    print_info(f"Dominio: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Conexión": False,
        "Mobile Login": False,
        "Arduino Data": False,
        "Mobile Reporte": False,
        "Register": False,
        "List Users": False,
        "CORS": False
    }
    
    # Test 1: Conexión
    results["Conexión"] = test_api_connection()
    if not results["Conexión"]:
        print_error("\n⚠️  El servidor no está accesible. Abortando pruebas...")
        return results
    
    time.sleep(1)
    
    # Test 2: Mobile Login
    success, _ = test_mobile_login()
    results["Mobile Login"] = success
    time.sleep(1)
    
    # Test 3: Arduino Data
    success, _ = test_arduino_data()
    results["Arduino Data"] = success
    time.sleep(1)
    
    # Test 4: Mobile Reporte
    success, _ = test_mobile_reporte()
    results["Mobile Reporte"] = success
    time.sleep(1)
    
    # Test 5: Register
    success, _ = test_api_register()
    results["Register"] = success
    time.sleep(1)
    
    # Test 6: List Users
    success, _ = test_api_listar()
    results["List Users"] = success
    time.sleep(1)
    
    # Test 7: CORS
    results["CORS"] = test_cors_headers()
    
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
    elif passed >= total * 0.7:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  {total - passed} pruebas fallaron{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Múltiples fallos detectados{Colors.END}")
    
    return results

if __name__ == "__main__":
    try:
        # Desactivar warnings SSL para desarrollo
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.END}")
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
