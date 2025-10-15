import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line, call_command
import subprocess
import json

def migrate_sqlite_to_postgres():
    """
    Script para migrar datos de SQLite a PostgreSQL
    """
    print("🔄 Iniciando migración de SQLite a PostgreSQL...")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cardiaco_vaca.settings')
    django.setup()
    
    # Paso 1: Hacer backup de SQLite
    print("📁 Paso 1: Creando backup de datos SQLite...")
    try:
        call_command('dumpdata', 
                    '--natural-foreign', 
                    '--natural-primary', 
                    '--exclude=contenttypes', 
                    '--exclude=auth.permission',
                    '--exclude=admin.logentry',
                    '--exclude=sessions.session',
                    '--indent=2',
                    output='sqlite_data_backup.json')
        print("✅ Backup de SQLite creado: sqlite_data_backup.json")
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return False
    
    # Paso 2: Verificar el archivo de backup
    if not os.path.exists('sqlite_data_backup.json'):
        print("❌ No se pudo crear el archivo de backup")
        return False
    
    # Mostrar estadísticas del backup
    with open('sqlite_data_backup.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"📊 Registros a migrar: {len(data)}")
        
        # Mostrar modelos que se van a migrar
        models = {}
        for item in data:
            model = item['model']
            models[model] = models.get(model, 0) + 1
        
        print("📋 Modelos a migrar:")
        for model, count in models.items():
            print(f"   - {model}: {count} registros")
    
    print("\n🎯 Backup completado exitosamente!")
    print("\n📝 Próximos pasos para completar la migración:")
    print("1. Configura PostgreSQL localmente")
    print("2. Crea una base de datos llamada 'controlbovino_local'")
    print("3. Ejecuta: python migrate_to_postgres.py --load")
    
    return True

def load_data_to_postgres():
    """
    Cargar datos a PostgreSQL
    """
    print("🔄 Cargando datos a PostgreSQL...")
    # Depuración: mostrar valor de DATABASE_URL
    print("DEBUG: DATABASE_URL=", os.environ.get("DATABASE_URL", "<NO DEFINIDA>"))
    
    # Cambiar a settings de PostgreSQL
    os.environ['DJANGO_SETTINGS_MODULE'] = 'cardiaco_vaca.settings_postgres'
    django.setup()
    
    try:
        # Ejecutar migraciones
        print("📦 Ejecutando migraciones...")
        call_command('migrate')

        # Cargar datos desde el archivo JSON explícitamente
        fixture_path = 'sqlite_data_backup.json'
        if not os.path.exists(fixture_path):
            print(f"❌ El archivo de backup '{fixture_path}' no se encuentra en el directorio actual: {os.getcwd()}")
            return False
        print(f"📥 Cargando datos desde '{fixture_path}'...")
        call_command('loaddata', fixture_path)

        print("✅ Migración completada exitosamente!")
        return True

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--load':
        load_data_to_postgres()
    else:
        migrate_sqlite_to_postgres()