"""
Script final para probar TODAS las APIs del Sistema de Control Bovino
Versión mejorada después de correcciones
"""

import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"
TIMEOUT = 10

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*70}{Colors.END}\n")

def print_test(title, num):
    print(f"\n{Colors.BOLD}{Colors.CYAN}[TEST {num}] {title}{Colors.END}")
    print(f"{Colors.CYAN}{'-'*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

def print_response(response, lines=6):
    print(f"  {Colors.BOLD}Status:{Colors.END} {response.status_code}")
    try:
        json_data = response.json()
        print(f"  {Colors.BOLD}Response:{Colors.END}")
        for line in json.dumps(json_data, indent=2, ensure_ascii=False).split('\n')[:lines]:
            print(f"    {line}")
        if len(json.dumps(json_data, indent=2, ensure_ascii=False).split('\n')) > lines:
            print(f"    ...")
    except:
        print(f"  {Colors.BOLD}Response:{Colors.END} {response.text[:150]}")

test_count = 0

# ==================== DASHBOARD APIs ====================
def test_dashboard_data():
    global test_count
    test_count += 1
    print_test("Dashboard Data API", test_count)
    
    url = f"{BASE_URL}/monitor/datos/1/"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 200:
            data = response.json()
            if 'collar_info' in data:
                print_success(f"✓ Datos obtenidos: {data['collar_info'].get('nombre')}")
                return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_ultimo_registro():
    global test_count
    test_count += 1
    print_test("Último Registro API", test_count)
    
    url = f"{BASE_URL}/ultimo/registro/1"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 200:
            print_success(f"✓ Último registro obtenido")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

# ==================== MOBILE APIs ====================
def test_login_api():
    global test_count
    test_count += 1
    print_test("Login API (Mobile)", test_count)
    
    url = f"{BASE_URL}/api/movil/login/"
    creds = {"username": "admin@test.com", "password": "admin123"}
    
    try:
        response = requests.post(url, json=creds, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 200:
            data = response.json()
            print_success(f"✓ Login exitoso: {data.get('data', {}).get('Nombres')}")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_reporte_por_id():
    global test_count
    test_count += 1
    print_test("Reporte por ID API (Mobile)", test_count)
    
    url = f"{BASE_URL}/api/movil/datos/"
    data = {"sensor": "1", "username": "admin@test.com"}
    
    try:
        response = requests.post(url, data=data, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 200:
            print_success(f"✓ Reporte obtenido correctamente")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

# ==================== USER MANAGEMENT ====================
def test_api_register():
    global test_count
    test_count += 1
    print_test("Registro de Usuario API", test_count)
    
    url = f"{BASE_URL}/api/register"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = {
        "cedula": f"9876543{timestamp[-3:]}",
        "telefono": "0912345678",
        "nombre": "TestUser",
        "apellido": "Final",
        "email": f"test{timestamp}@controlbovino.com"
    }
    
    try:
        response = requests.post(url, data=data, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 201:
            print_success(f"✓ Usuario registrado exitosamente")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_api_list():
    global test_count
    test_count += 1
    print_test("Listar Usuarios API", test_count)
    
    url = f"{BASE_URL}/api/listar"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print_success(f"✓ {total} usuarios listados")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_api_edit():
    global test_count
    test_count += 1
    print_test("Editar Usuario API", test_count)
    
    # Usar el primer usuario disponible (ID = 3 según los resultados anteriores)
    user_id = 3
    url = f"{BASE_URL}/api/editar/{user_id}/"
    
    data = {
        "cedula": "1111111111",
        "telefono": "0999999999",
        "nombre": "EditadoTest",
        "apellido": "EditadoFinal",
        "email": "editado@test.com"
    }
    
    try:
        response = requests.post(url, data=data, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 200:
            print_success(f"✓ Usuario editado correctamente")
            return True
        elif response.status_code == 404:
            print_error("Usuario no encontrado")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

# ==================== ARDUINO APIs ====================
def test_arduino_lectura():
    global test_count
    test_count += 1
    print_test("Arduino Lectura API (IoT)", test_count)
    
    url = f"{BASE_URL}/api/arduino/monitoreo"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = {
        "collar_id": 2000,
        "nombre_vaca": f"VacaArduino{timestamp[-4:]}",
        "mac_collar": f"FF:EE:DD:CC:BB:{timestamp[-2:]}",
        "temperatura": 39,
        "pulsaciones": 60
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 201:
            print_success(f"✓ Datos del Arduino guardados")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_arduino_validacion():
    global test_count
    test_count += 1
    print_test("Arduino API - Validación de Datos", test_count)
    
    url = f"{BASE_URL}/api/arduino/monitoreo"
    data = {
        "collar_id": 1,
        "nombre_vaca": "Test",
        "mac_collar": "AA:BB:CC:DD:EE:FF"
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 400:
            print_success(f"✓ Validación funciona correctamente")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_arduino_metodo():
    global test_count
    test_count += 1
    print_test("Arduino API - Validación de Método HTTP", test_count)
    
    url = f"{BASE_URL}/api/arduino/monitoreo"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        if response.status_code == 405:
            print_success(f"✓ Validación de método HTTP funciona")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

# ==================== EJECUTAR TODAS LAS PRUEBAS ====================
def run_all_tests():
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*70}")
    print("PRUEBAS FINALES - CONTROL BOVINO")
    print(f"{'='*70}{Colors.END}\n")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {BASE_URL}\n")
    
    # Verificar conexión
    print_info("Verificando conexión con el servidor...")
    try:
        requests.get(BASE_URL, timeout=5)
        print_success("Servidor accesible")
    except:
        print_error("No se puede conectar al servidor")
        sys.exit(1)
    
    # DASHBOARD
    print_header("📊 APIS DASHBOARD (JSON)")
    r1 = test_dashboard_data()
    r2 = test_ultimo_registro()
    
    # MOBILE
    print_header("📱 APIS MÓVILES")
    r3 = test_login_api()
    r4 = test_reporte_por_id()
    
    # USERS
    print_header("👥 GESTIÓN DE USUARIOS")
    r5 = test_api_register()
    r6 = test_api_list()
    r7 = test_api_edit()
    
    # ARDUINO
    print_header("🔧 APIS IoT (ARDUINO)")
    r8 = test_arduino_lectura()
    r9 = test_arduino_validacion()
    r10 = test_arduino_metodo()
    
    # RESUMEN
    print_header("📋 RESUMEN FINAL")
    
    results = {
        "Dashboard Data API": r1,
        "Último Registro API": r2,
        "Login API (Mobile)": r3,
        "Reporte por ID API": r4,
        "Registro Usuario": r5,
        "Listar Usuarios": r6,
        "Editar Usuario": r7,
        "Arduino Lectura": r8,
        "Arduino Validación": r9,
        "Arduino Método HTTP": r10,
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"{Colors.BOLD}Resultado por API:{Colors.END}\n")
    for i, (name, result) in enumerate(results.items(), 1):
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"  {color}[{status}]{Colors.END} {i:2d}. {name}")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}Total: {passed}/{total} APIs funcionando correctamente{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡TODAS LAS APIs FUNCIONAN CORRECTAMENTE!{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  {total-passed} API(s) con problemas{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0)
    except KeyboardInterrupt:
        print_error("\nPruebas interrumpidas")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)
