#!/usr/bin/env python
"""
Script para preparar migración directa a Render
"""
import os
import django
from django.core.management import call_command

def export_for_render():
    """Exportar datos para migración directa a Render"""
    
    print("🔄 Preparando datos para migración a Render...")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cardiaco_vaca.settings')
    django.setup()
    
    # Exportar solo los datos de la aplicación
    try:
        call_command('dumpdata', 
                    'temp_car',  # Solo tu aplicación
                    '--natural-foreign', 
                    '--natural-primary', 
                    '--indent=2',
                    output='render_migration_data.json')
        
        print("✅ Datos exportados: render_migration_data.json")
        print("📋 Este archivo contiene todos los datos de tu aplicación")
        print("\n🚀 Pasos siguientes:")
        print("1. Sube este archivo al repositorio")
        print("2. Despliega en Render") 
        print("3. Ejecuta en Render: python manage.py loaddata render_migration_data.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    export_for_render()