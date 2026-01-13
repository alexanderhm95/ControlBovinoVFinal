"""
Script para probar todas las APIs del Sistema de Control Bovino
Prueba los siguientes endpoints:
1. Dashboard APIs - datos de collares y monitoreo
2. Mobile APIs - login, reportes, CRUD usuarios  
3. Arduino API - recepción de datos de sensores
"""

import requests
import json
from datetime import datetime
import sys

# Configuración base
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(title):
    """Imprime el título de la prueba"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    """Imprime mensaje informativo"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

def print_response(response):
    """Imprime detalles de la respuesta"""
    print(f"  Status: {response.status_code}")
    try:
        print(f"  Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"  Response: {response.text[:200]}")


# ==========================================
# 1. PRUEBAS DE DASHBOARD APIs (Web)
# ==========================================

def test_dashboard_data():
    """Prueba el endpoint de datos del dashboard"""
    print_test("TEST 1: Dashboard Data API")
    
    # Probar con collar_id = 1
    collar_id = 1
    url = f"{BASE_URL}/monitor/datos/{collar_id}/"
    
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if 'collar_info' in data:
                print_success(f"Datos obtenidos correctamente para collar {collar_id}")
                print_info(f"Bovino: {data['collar_info'].get('nombre', 'N/A')}")
                print_info(f"Temperatura: {data['collar_info'].get('temperatura', 'N/A')}°C")
                print_info(f"Pulsaciones: {data['collar_info'].get('pulsaciones', 'N/A')} bpm")
                return True
        elif response.status_code == 404:
            print_error(f"Collar {collar_id} no encontrado o sin lecturas")
        else:
            print_error(f"Error en respuesta: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print_error("No se pudo conectar al servidor. ¿Está el servidor corriendo?")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        return False
    
    return False


def test_ultimo_registro():
    """Prueba el endpoint del último registro"""
    print_test("TEST 2: Último Registro API")
    
    collar_id = 1
    url = f"{BASE_URL}/ultimo/registro/{collar_id}"
    
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Último registro obtenido correctamente")
            print_info(f"Fecha: {data.get('fecha_lectura', 'N/A')}")
            print_info(f"Hora: {data.get('hora_lectura', 'N/A')}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


# ==========================================
# 2. PRUEBAS DE MOBILE APIs
# ==========================================

def test_login_api():
    """Prueba el endpoint de login de la app móvil"""
    print_test("TEST 3: Login API (Mobile)")
    
    url = f"{BASE_URL}/api/movil/login/"
    
    # Intentar con credenciales de prueba
    test_credentials = [
        {"username": "admin@test.com", "password": "admin123"},
        {"username": "test@test.com", "password": "test123"},
    ]
    
    for creds in test_credentials:
        print_info(f"\nIntentando login con: {creds['username']}")
        
        try:
            response = requests.post(url, json=creds, timeout=TIMEOUT)
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Login exitoso: {data.get('data', {}).get('Nombres', 'N/A')}")
                return True, data.get('data', {})
            elif response.status_code == 401:
                print_error("Credenciales incorrectas")
            else:
                print_error(f"Error: {response.status_code}")
                
        except Exception as e:
            print_error(f"Error: {str(e)}")
    
    print_info("Prueba de login con credenciales inválidas")
    response = requests.post(url, json={"username": "invalid", "password": "wrong"}, timeout=TIMEOUT)
    if response.status_code == 401:
        print_success("Validación de credenciales inválidas funciona correctamente")
    
    return False, None


def test_reporte_por_id():
    """Prueba el endpoint de reportes por ID (requiere autenticación)"""
    print_test("TEST 4: Reporte por ID API (Mobile)")
    
    url = f"{BASE_URL}/api/movil/datos/"
    
    # Datos de prueba
    data = {
        "sensor": "1",  # collar_id
        "username": "admin@test.com"
    }
    
    try:
        response = requests.post(url, data=data, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Reporte obtenido correctamente")
            if 'reporte' in result:
                print_info(f"Bovino: {result['reporte'].get('nombre_vaca', 'N/A')}")
                print_info(f"Registrado: {result['reporte'].get('registrado', False)}")
            return True
        elif response.status_code == 404:
            print_error("Bovino o usuario no encontrado")
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


def test_api_list():
    """Prueba el endpoint de listado de usuarios"""
    print_test("TEST 5: Listar Usuarios API")
    
    url = f"{BASE_URL}/api/listar"
    
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Usuarios listados: {data.get('total', 0)}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


def test_api_register():
    """Prueba el endpoint de registro de usuarios"""
    print_test("TEST 6: Registro de Usuario API")
    
    url = f"{BASE_URL}/api/register"
    
    # Datos de prueba con timestamp para evitar duplicados
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = {
        "cedula": f"1234567{timestamp[-3:]}",
        "telefono": "0987654321",
        "nombre": "Usuario",
        "apellido": "Prueba",
        "email": f"prueba{timestamp}@test.com"
    }
    
    try:
        response = requests.post(url, data=data, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 201:
            print_success("Usuario registrado exitosamente")
            return True
        elif response.status_code == 400:
            result = response.json()
            if 'Email ya registrado' in str(result):
                print_info("Email ya existe (comportamiento esperado)")
                return True
            else:
                print_error(f"Error de validación: {result}")
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


# ==========================================
# 3. PRUEBAS DE ARDUINO API (IoT)
# ==========================================

def test_arduino_lectura():
    """Prueba el endpoint de lectura del Arduino"""
    print_test("TEST 7: Arduino Lectura API (IoT)")
    
    url = f"{BASE_URL}/api/arduino/monitoreo"
    
    # Simular datos del Arduino
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = {
        "collar_id": 999,  # ID de prueba
        "nombre_vaca": f"Vaca Prueba {timestamp[-4:]}",
        "mac_collar": f"AA:BB:CC:DD:EE:{timestamp[-2:]}",
        "temperatura": 38,
        "pulsaciones": 55
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 201:
            result = response.json()
            print_success("Datos del Arduino guardados correctamente")
            print_info(f"Lectura ID: {result.get('data', {}).get('lectura_id', 'N/A')}")
            print_info(f"Bovino nuevo: {result.get('data', {}).get('bovino_nuevo', False)}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


def test_arduino_lectura_incompleta():
    """Prueba el endpoint con datos incompletos"""
    print_test("TEST 8: Arduino API - Validación de Datos")
    
    url = f"{BASE_URL}/api/arduino/monitoreo"
    
    # Datos incompletos (falta temperatura)
    data = {
        "collar_id": 1,
        "nombre_vaca": "Vaca Test",
        "mac_collar": "AA:BB:CC:DD:EE:FF"
        # falta temperatura
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 400:
            print_success("Validación de datos incompletos funciona correctamente")
            return True
        else:
            print_error(f"Se esperaba código 400, se obtuvo: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


# ==========================================
# EJECUTAR TODAS LAS PRUEBAS
# ==========================================

def run_all_tests():
    """Ejecuta todas las pruebas y genera un reporte"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("SISTEMA DE PRUEBAS - CONTROL BOVINO API")
    print(f"{'='*60}{Colors.END}\n")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}\n")
    
    # Verificar conexión
    print_info("Verificando conexión con el servidor...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print_success("Servidor accesible")
    except:
        print_error("No se puede conectar al servidor")
        print_error("Asegúrese de que el servidor Django esté corriendo")
        print_info("Ejecute: python manage.py runserver")
        sys.exit(1)
    
    # Ejecutar pruebas
    results = {
        "Dashboard Data": test_dashboard_data(),
        "Último Registro": test_ultimo_registro(),
        "Login API": test_login_api()[0],
        "Reporte por ID": test_reporte_por_id(),
        "Listar Usuarios": test_api_list(),
        "Registro Usuario": test_api_register(),
        "Arduino Lectura": test_arduino_lectura(),
        "Arduino Validación": test_arduino_lectura_incompleta(),
    }
    
    # Resumen de resultados
    print_test("RESUMEN DE PRUEBAS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status:6}{Colors.END} - {test_name}")
    
    print(f"\n{Colors.BOLD}Resultado: {passed}/{total} pruebas exitosas{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}¡Todas las pruebas pasaron!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}Algunas pruebas fallaron. Revise los detalles arriba.{Colors.END}")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\nPruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error fatal: {str(e)}")
        sys.exit(1)
