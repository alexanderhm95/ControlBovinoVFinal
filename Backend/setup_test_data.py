"""
Script para configurar datos de prueba en la base de datos
Crea usuarios y datos necesarios para las pruebas de API
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cardiaco_vaca.settings')
django.setup()

from django.contrib.auth.models import User
from temp_car.models import PersonalInfo, Bovinos, Temperatura, Pulsaciones, Lectura
from datetime import datetime

def create_test_users():
    """Crea usuarios de prueba"""
    print("📝 Creando usuarios de prueba...")
    
    # Usuario admin
    if not User.objects.filter(username='admin@test.com').exists():
        user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            is_staff=False
        )
        
        PersonalInfo.objects.create(
            cedula='1234567890',
            telefono='0987654321',
            nombre='Admin',
            apellido='Test',
            email='admin@test.com'
        )
        print(f"  ✓ Usuario admin@test.com creado (password: admin123)")
    else:
        print(f"  ℹ Usuario admin@test.com ya existe")
    
    # Usuario test
    if not User.objects.filter(username='test@test.com').exists():
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='test123',
            first_name='Test',
            last_name='User',
            is_staff=False
        )
        
        PersonalInfo.objects.create(
            cedula='0987654321',
            telefono='0912345678',
            nombre='Test',
            apellido='User',
            email='test@test.com'
        )
        print(f"  ✓ Usuario test@test.com creado (password: test123)")
    else:
        print(f"  ℹ Usuario test@test.com ya existe")

def verify_bovinos():
    """Verifica que existan bovinos de prueba"""
    print("\n🐄 Verificando bovinos...")
    
    bovinos_count = Bovinos.objects.filter(activo=True).count()
    print(f"  ℹ Bovinos activos: {bovinos_count}")
    
    if bovinos_count == 0:
        print("  ⚠ No hay bovinos activos, creando uno de prueba...")
        bovino = Bovinos.objects.create(
            idCollar=1,
            macCollar='AA:BB:CC:DD:EE:FF',
            nombre='Vaca Prueba',
            fecha_registro=datetime.now(),
            activo=True
        )
        
        # Crear una lectura de prueba
        temp = Temperatura.objects.create(valor=38)
        puls = Pulsaciones.objects.create(valor=55)
        
        Lectura.objects.create(
            id_Temperatura=temp,
            id_Pulsaciones=puls,
            id_Bovino=bovino,
            fecha_lectura=datetime.now().date(),
            hora_lectura=datetime.now().time()
        )
        print(f"  ✓ Bovino de prueba creado (ID: {bovino.idCollar})")
    else:
        primer_bovino = Bovinos.objects.filter(activo=True).first()
        print(f"  ✓ Bovino disponible: {primer_bovino.nombre} (ID: {primer_bovino.idCollar})")

def main():
    """Ejecuta la configuración de datos de prueba"""
    print("\n" + "="*60)
    print("CONFIGURACIÓN DE DATOS DE PRUEBA")
    print("="*60 + "\n")
    
    try:
        create_test_users()
        verify_bovinos()
        
        print("\n" + "="*60)
        print("✓ Configuración completada exitosamente")
        print("="*60)
        print("\nCredenciales de prueba:")
        print("  Usuario 1: admin@test.com / admin123")
        print("  Usuario 2: test@test.com / test123")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
