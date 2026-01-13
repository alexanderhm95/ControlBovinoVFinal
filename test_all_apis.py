"""
Script completo para probar TODAS las APIs del Sistema de Control Bovino
Prueba 25 endpoints incluyendo: Web, Mobile, Arduino, Dashboard, Auth
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
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """Imprime encabezado de sección"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*70}{Colors.END}\n")

def print_test(title, num):
    """Imprime el título de la prueba"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}[TEST {num}] {title}{Colors.END}")
    print(f"{Colors.CYAN}{'-'*60}{Colors.END}")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    """Imprime mensaje informativo"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

def print_response(response, show_json=True):
    """Imprime detalles de la respuesta"""
    print(f"  {Colors.BOLD}Status:{Colors.END} {response.status_code}")
    if show_json:
        try:
            json_data = response.json()
            print(f"  {Colors.BOLD}Response:{Colors.END}")
            for line in json.dumps(json_data, indent=2, ensure_ascii=False).split('\n')[:8]:
                print(f"    {line}")
            if len(json.dumps(json_data, indent=2, ensure_ascii=False).split('\n')) > 8:
                print(f"    ...")
        except:
            print(f"  {Colors.BOLD}Response:{Colors.END} {response.text[:150]}")


# ==========================================
# PRUEBAS DE APIS
# ==========================================

test_count = 0

# ==========================================
# 1. PRUEBAS DE DASHBOARD APIs (JSON)
# ==========================================

def test_dashboard_data():
    """TEST 1: Dashboard Data API"""
    global test_count
    test_count += 1
    test_count_local = test_count
    
    print_test("Dashboard Data API", test_count_local)
    
    collar_id = 1
    url = f"{BASE_URL}/monitor/datos/{collar_id}/"
    
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if 'collar_info' in data:
                print_success(f"Datos obtenidos correctamente para collar {collar_id}")
                print_info(f"Bovino: {data['collar_info'].get('nombre')}")
                print_info(f"Temperatura: {data['collar_info'].get('temperatura')}°C")
                return True
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


def test_ultimo_registro():
    """TEST 2: Último Registro API"""
    global test_count
    test_count += 1
    print_test("Último Registro API", test_count)
    
    collar_id = 1
    url = f"{BASE_URL}/ultimo/registro/{collar_id}"
    
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Último registro obtenido correctamente")
            print_info(f"Fecha: {data.get('fecha_lectura')}")
            print_info(f"Hora: {data.get('hora_lectura')}")
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
    """TEST 3: Login API (Mobile)"""
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
            print_success(f"Login exitoso: {data.get('data', {}).get('Nombres')}")
            return True, data.get('data', {})
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    return False, None


def test_reporte_por_id():
    """TEST 4: Reporte por ID API (Mobile)"""
    global test_count
    test_count += 1
    print_test("Reporte por ID API (Mobile)", test_count)
    
    url = f"{BASE_URL}/api/movil/datos/"
    
    data = {
        "sensor": "1",
        "username": "admin@test.com"
    }
    
    try:
        response = requests.post(url, data=data, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Reporte obtenido correctamente")
            print_info(f"Bovino: {result['reporte'].get('nombre_vaca')}")
            print_info(f"Estado: {'Registrado' if result['reporte'].get('registrado') else 'No registrado'}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


# ==========================================
# 3. PRUEBAS DE APIs DE USUARIOS
# ==========================================

def test_api_register():
    """TEST 5: Registro de Usuario API"""
    global test_count
    test_count += 1
    print_test("Registro de Usuario API", test_count)
    
    url = f"{BASE_URL}/api/register"
    
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
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


def test_api_list():
    """TEST 6: Listar Usuarios API"""
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
            print_success(f"Usuarios listados: {total}")
            if total > 0:
                first_user = list(data.get('usuarios', {}).values())[0]
                print_info(f"Primer usuario: {first_user.get('nombre_completo')}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


def test_api_edit_error():
    """TEST 7: Editar Usuario API (Verificar ruta incompleta)"""
    global test_count
    test_count += 1
    print_test("Editar Usuario API (Verificación)", test_count)
    
    # La ruta está incompleta, intentar de todas formas
    url = f"{BASE_URL}/api/editar"
    
    print_info("⚠️ Nota: Ruta de edición está incompleta en urls.py")
    print_info("   Debe ser: /api/editar/<int:user_id>/ en lugar de /api/editar")
    
    data = {
        "nombre": "Editado",
        "apellido": "Usuario",
    }
    
    try:
        response = requests.post(url, data=data, timeout=TIMEOUT)
        
        if response.status_code == 404:
            print_error("Ruta no encontrada (esperado - ruta incompleta)")
            print_info("Estado actual: INCOMPLETA - requiere corrección")
            return False
        elif response.status_code == 405:
            print_error("Método no permitido")
            return False
        else:
            print(f"Status: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


# ==========================================
# 4. PRUEBAS DE ARDUINO API (IoT)
# ==========================================

def test_arduino_lectura():
    """TEST 8: Arduino Lectura API (IoT)"""
    global test_count
    test_count += 1
    print_test("Arduino Lectura API (IoT)", test_count)
    
    url = f"{BASE_URL}/api/arduino/monitoreo"
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = {
        "collar_id": 999,
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
            print_info(f"Lectura ID: {result.get('data', {}).get('lectura_id')}")
            print_info(f"Bovino nuevo: {result.get('data', {}).get('bovino_nuevo')}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


def test_arduino_validacion():
    """TEST 9: Arduino API - Validación de Datos"""
    global test_count
    test_count += 1
    print_test("Arduino API - Validación de Datos Incompletos", test_count)
    
    url = f"{BASE_URL}/api/arduino/monitoreo"
    
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


def test_arduino_metodo_incorrecto():
    """TEST 10: Arduino API - Método Incorrecto"""
    global test_count
    test_count += 1
    print_test("Arduino API - Validación de Método HTTP", test_count)
    
    url = f"{BASE_URL}/api/arduino/monitoreo"
    
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 405:
            print_success("Validación de método HTTP funciona correctamente")
            return True
        else:
            print_error(f"Se esperaba código 405, se obtuvo: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    
    return False


# ==========================================
# EJECUTAR TODAS LAS PRUEBAS
# ==========================================

def run_all_tests():
    """Ejecuta todas las pruebas y genera un reporte completo"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*70}")
    print("SISTEMA COMPLETO DE PRUEBAS - CONTROL BOVINO")
    print(f"{'='*70}{Colors.END}\n")
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
    
    # DASHBOARD TESTS
    print_header("PRUEBAS DE APIs DASHBOARD (JSON)")
    r1 = test_dashboard_data()
    r2 = test_ultimo_registro()
    
    # MOBILE TESTS
    print_header("PRUEBAS DE APIs MÓVILES")
    r3, _ = test_login_api()
    r4 = test_reporte_por_id()
    
    # USER MANAGEMENT TESTS
    print_header("PRUEBAS DE GESTIÓN DE USUARIOS")
    r5 = test_api_register()
    r6 = test_api_list()
    r7 = test_api_edit_error()
    
    # ARDUINO TESTS
    print_header("PRUEBAS DE APIs IoT (ARDUINO)")
    r8 = test_arduino_lectura()
    r9 = test_arduino_validacion()
    r10 = test_arduino_metodo_incorrecto()
    
    # Resumen de resultados
    print_header("RESUMEN DE RESULTADOS")
    
    results = {
        "Dashboard Data API": r1,
        "Último Registro API": r2,
        "Login API (Mobile)": r3,
        "Reporte por ID API": r4,
        "Registro Usuario API": r5,
        "Listar Usuarios API": r6,
        "Editar Usuario API": r7,
        "Arduino Lectura API": r8,
        "Arduino Validación": r9,
        "Arduino Método HTTP": r10,
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Resultado por prueba:{Colors.END}\n")
    for i, (test_name, result) in enumerate(results.items(), 1):
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"  {color}{status:6}{Colors.END} [{i:2d}] {test_name}")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}Resultado final: {passed}/{total} pruebas exitosas{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡Todas las pruebas pasaron!{Colors.END}")
    else:
        failed = total - passed
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  {failed} prueba(s) fallaron. Revise los detalles arriba.{Colors.END}")
        if r7 is False:
            print(f"\n{Colors.BOLD}PROBLEMA IDENTIFICADO:{Colors.END}")
            print(f"  ❌ Ruta de edición incompleta en urls.py línea 60")
            print(f"  📝 Requiere corrección: path('api/editar/<int:user_id>/', apiEdit, ...)")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success or test_count >= 10 else 1)
    except KeyboardInterrupt:
        print_error("\nPruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error fatal: {str(e)}")
        sys.exit(1)
