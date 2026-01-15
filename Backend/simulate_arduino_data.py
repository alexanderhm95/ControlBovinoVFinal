#!/usr/bin/env python3
"""
Script para simular datos de Arduino (collares inteligentes)
Simula 20 minutos de monitoreo de 2 bovinos
Envía datos cada 10 segundos como haría el Arduino real
"""

import requests
import time
import random
import json
from datetime import datetime, timedelta
import sys

# Configuración
BASE_URL = "http://localhost:8081"
API_ENDPOINT = "/api/arduino/monitoreo"
SIMULATION_DURATION = 1200  # 20 minutos en segundos
SEND_INTERVAL = 10  # Enviar datos cada 10 segundos (como Arduino real)

# Collares para simular
COLLARES = {
    2: {
        "nombre": "Salome",
        "mac": "AA:BB:CC:DD:EE:02",
        "temp_base": 37.8,
        "pulsaciones_base": 75
    },
    3: {
        "nombre": "Sofia",
        "mac": "AA:BB:CC:DD:EE:03",
        "temp_base": 38.0,
        "pulsaciones_base": 80
    }
}

class ArduinoSimulator:
    """Simula sensores Arduino y envía datos al servidor"""
    
    def __init__(self, base_url, endpoint):
        self.base_url = base_url
        self.endpoint = endpoint
        self.total_sent = 0
        self.total_errors = 0
        self.start_time = datetime.now()
    
    def get_realistic_value(self, base_value, variation=1.0):
        """Genera valores realistas con pequeñas variaciones"""
        return round(base_value + random.uniform(-variation, variation), 1)
    
    def get_temperature(self, collar_id):
        """Simula lectura de temperatura"""
        base = COLLARES[collar_id]["temp_base"]
        # Temperatura varía entre 36.5 y 39.5°C
        return self.get_realistic_value(base, variation=1.5)
    
    def get_heart_rate(self, collar_id):
        """Simula frecuencia cardíaca"""
        base = COLLARES[collar_id]["pulsaciones_base"]
        # Pulsaciones varían entre 50 y 120 bpm
        return int(self.get_realistic_value(base, variation=15))
    
    def send_data(self, collar_id):
        """Envía datos de un collar al servidor"""
        collar_info = COLLARES[collar_id]
        
        # Generar datos simulados
        temperatura = self.get_temperature(collar_id)
        pulsaciones = self.get_heart_rate(collar_id)
        
        # Crear payload JSON (igual a Arduino)
        payload = {
            "collar_id": str(collar_id),
            "temperatura": temperatura,
            "nombre_vaca": collar_info["nombre"],
            "pulsaciones": pulsaciones,
            "mac_collar": collar_info["mac"]
        }
        
        try:
            # Enviar POST request
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "ArduinoSimulator/1.0",
                    "Authorization": "Bearer sk_arduino_controlbovino_2024"
                },
                timeout=5
            )
            
            # Log del envío
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_icon = "✅" if response.status_code == 200 else "⚠️"
            
            print(f"{status_icon} [{timestamp}] Collar {collar_id} ({collar_info['nombre']}): "
                  f"Temp={temperatura}°C, Puls={pulsaciones}bpm → HTTP {response.status_code}")
            
            if response.status_code == 200:
                self.total_sent += 1
                return True
            else:
                self.total_errors += 1
                print(f"   Respuesta: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.total_errors += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"❌ [{timestamp}] Error enviando datos del collar {collar_id}: {str(e)}")
            return False
    
    def run_simulation(self):
        """Ejecuta la simulación de 20 minutos"""
        print("\n" + "="*70)
        print("🤖 SIMULADOR DE DATOS ARDUINO - CONTROL BOVINO")
        print("="*70)
        print(f"📍 Servidor: {self.base_url}")
        print(f"📊 Endpoint: {self.endpoint}")
        print(f"⏱️  Duración: 20 minutos (1200 segundos)")
        print(f"📤 Intervalo de envío: {SEND_INTERVAL} segundos")
        print(f"🐄 Collares a simular: {len(COLLARES)}")
        
        for collar_id, info in COLLARES.items():
            print(f"   - Collar {collar_id}: {info['nombre']} (MAC: {info['mac']})")
        
        print("\n📋 Iniciando simulación...\n")
        
        elapsed_time = 0
        send_count = 0
        
        try:
            while elapsed_time < SIMULATION_DURATION:
                # Enviar datos de ambos collares
                for collar_id in COLLARES.keys():
                    self.send_data(collar_id)
                
                send_count += 1
                
                # Mostrar progreso cada 100 segundos
                if send_count % 10 == 0:
                    minutes = elapsed_time / 60
                    print(f"\n⏳ Progreso: {minutes:.1f} minutos completados\n")
                
                # Esperar antes del siguiente envío
                elapsed_time += SEND_INTERVAL
                if elapsed_time < SIMULATION_DURATION:
                    time.sleep(SEND_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulación interrumpida por el usuario")
        
        finally:
            self.print_summary()
    
    def print_summary(self):
        """Imprime resumen de la simulación"""
        elapsed = datetime.now() - self.start_time
        
        print("\n" + "="*70)
        print("📊 RESUMEN DE SIMULACIÓN")
        print("="*70)
        print(f"✅ Datos enviados exitosamente: {self.total_sent}")
        print(f"❌ Errores durante envío: {self.total_errors}")
        print(f"⏱️  Tiempo real de ejecución: {elapsed}")
        print(f"📦 Total de registros: {self.total_sent + self.total_errors}")
        
        if self.total_sent > 0:
            print(f"\n✨ Simulación completada correctamente")
            print(f"   Los datos están disponibles en:")
            print(f"   - API: {self.base_url}/api/movil/datos/2/ (Salome)")
            print(f"   - API: {self.base_url}/api/movil/datos/3/ (Sofia)")
            print(f"   - Dashboard: {self.base_url}/monitoreo_actual/")
        
        print("="*70 + "\n")


def main():
    """Función principal"""
    print("\n🔍 Verificando conexión al servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/movil/login/", timeout=5)
        print(f"✅ Servidor disponible (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Error: No se puede conectar al servidor en {BASE_URL}")
        print(f"   Detalles: {str(e)}")
        print(f"\n💡 Asegúrate de que:")
        print(f"   1. PM2 está ejecutando django-app: pm2 list")
        print(f"   2. El servidor está en puerto 8081: curl http://localhost:8081")
        sys.exit(1)
    
    # Crear y ejecutar simulador
    simulator = ArduinoSimulator(BASE_URL, API_ENDPOINT)
    simulator.run_simulation()


if __name__ == "__main__":
    main()
