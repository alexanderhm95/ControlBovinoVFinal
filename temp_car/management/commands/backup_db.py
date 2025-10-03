import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
import subprocess


class Command(BaseCommand):
    help = 'Crear backup de la base de datos SQLite'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-commit',
            action='store_true',
            help='Automáticamente hacer commit y push del backup',
        )
        parser.add_argument(
            '--max-backups',
            type=int,
            default=30,
            help='Número máximo de backups a mantener (default: 30)',
        )

    def handle(self, *args, **options):
        # Configuración
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        db_path = settings.DATABASES['default']['NAME']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"db_backup_{timestamp}.sqlite3"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Crear directorio de backups si no existe
        os.makedirs(backup_dir, exist_ok=True)

        try:
            # Verificar si la base de datos existe
            if not os.path.exists(db_path):
                self.stdout.write(
                    self.style.ERROR(f'❌ Base de datos no encontrada: {db_path}')
                )
                return

            # Crear backup
            self.stdout.write('📁 Creando backup de la base de datos...')
            shutil.copy2(db_path, backup_path)
            
            # Verificar que el backup se creó correctamente
            if os.path.exists(backup_path):
                file_size = os.path.getsize(backup_path)
                size_mb = file_size / (1024 * 1024)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Backup creado: {backup_filename}')
                )
                self.stdout.write(f'📊 Tamaño: {size_mb:.2f} MB')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Error al crear el backup')
                )
                return

            # Limpiar backups antiguos
            self.cleanup_old_backups(backup_dir, options['max_backups'])

            # Git operations si se solicita
            if options['auto_commit']:
                self.git_commit_backup(backup_path)

            self.stdout.write(
                self.style.SUCCESS('🎉 Proceso de backup completado exitosamente')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante el backup: {str(e)}')
            )

    def cleanup_old_backups(self, backup_dir, max_backups):
        """Eliminar backups antiguos manteniendo solo los más recientes"""
        try:
            # Obtener todos los archivos de backup
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith('db_backup_') and filename.endswith('.sqlite3'):
                    filepath = os.path.join(backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # Ordenar por fecha (más reciente primero)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Eliminar backups excedentes
            if len(backup_files) > max_backups:
                files_to_delete = backup_files[max_backups:]
                for filepath, _ in files_to_delete:
                    os.remove(filepath)
                    self.stdout.write(f'🗑️ Eliminado backup antiguo: {os.path.basename(filepath)}')
                
                self.stdout.write(f'📋 Backups restantes: {len(backup_files) - len(files_to_delete)}')
            else:
                self.stdout.write(f'📋 Backups totales: {len(backup_files)}')

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Error al limpiar backups antiguos: {str(e)}')
            )

    def git_commit_backup(self, backup_path):
        """Hacer commit y push del backup al repositorio"""
        try:
            # Verificar si estamos en un repositorio git
            result = subprocess.run(['git', 'status'], 
                                  capture_output=True, text=True, cwd=settings.BASE_DIR)
            if result.returncode != 0:
                self.stdout.write(
                    self.style.WARNING('⚠️ No se detectó repositorio git')
                )
                return

            # Agregar el archivo al staging
            subprocess.run(['git', 'add', backup_path], cwd=settings.BASE_DIR)
            
            # Crear commit
            commit_message = f"Backup automático de base de datos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                  capture_output=True, text=True, cwd=settings.BASE_DIR)
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS('✅ Backup agregado al repositorio')
                )
                
                # Hacer push
                push_result = subprocess.run(['git', 'push'], 
                                          capture_output=True, text=True, cwd=settings.BASE_DIR)
                if push_result.returncode == 0:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Backup subido al repositorio remoto')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Error al hacer push al repositorio remoto')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ No hay cambios para hacer commit o error en git')
                )

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Error en operaciones git: {str(e)}')
            )