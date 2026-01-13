"""
Vistas para visualizar y gestionar logs
"""

import os
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from temp_car.logging_utils import get_log_files

logger = logging.getLogger('temp_car')

@login_required
@require_http_methods(["GET"])
def view_logs_dashboard(request):
    """Vista del dashboard de logs"""
    if not request.user.is_staff:
        return JsonResponse({
            'error': 'Acceso denegado',
            'detalle': 'Solo los administradores pueden ver los logs'
        }, status=403)
    
    try:
        log_files = get_log_files()
        
        # Leer contenido de cada archivo de log
        logs_content = {}
        for filename, info in log_files.items():
            try:
                with open(info['path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Mostrar las últimas 50 líneas
                    logs_content[filename] = {
                        'total_lines': len(lines),
                        'last_50_lines': lines[-50:] if lines else [],
                        'size': info['size'],
                    }
            except Exception as e:
                logs_content[filename] = {
                    'error': f'Error al leer archivo: {str(e)}'
                }
        
        return JsonResponse({
            'logs': logs_content,
            'log_files': list(log_files.keys()),
            'timestamp': str(__import__('datetime').datetime.now()),
        })
    
    except Exception as e:
        logger.error(f"Error al obtener logs: {str(e)}")
        return JsonResponse({
            'error': 'Error al obtener logs',
            'detalle': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_log_file(request, filename):
    """Descarga un archivo de log específico"""
    if not request.user.is_staff:
        return JsonResponse({
            'error': 'Acceso denegado',
            'detalle': 'Solo los administradores pueden descargar logs'
        }, status=403)
    
    try:
        log_files = get_log_files()
        
        if filename not in log_files:
            return JsonResponse({
                'error': 'Archivo de log no encontrado',
                'disponibles': list(log_files.keys())
            }, status=404)
        
        file_path = log_files[filename]['path']
        
        if not os.path.exists(file_path):
            return JsonResponse({
                'error': 'Archivo no existe'
            }, status=404)
        
        return FileResponse(
            open(file_path, 'rb'),
            content_type='text/plain',
            as_attachment=True,
            filename=filename
        )
    
    except Exception as e:
        logger.error(f"Error al descargar log: {str(e)}")
        return JsonResponse({
            'error': 'Error al descargar log',
            'detalle': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_log_content(request, filename):
    """Obtiene el contenido de un archivo de log en JSON"""
    if not request.user.is_staff:
        return JsonResponse({
            'error': 'Acceso denegado',
            'detalle': 'Solo los administradores pueden ver los logs'
        }, status=403)
    
    try:
        log_files = get_log_files()
        
        if filename not in log_files:
            return JsonResponse({
                'error': 'Archivo de log no encontrado',
                'disponibles': list(log_files.keys())
            }, status=404)
        
        file_path = log_files[filename]['path']
        lines_to_show = int(request.GET.get('lines', 50))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        return JsonResponse({
            'filename': filename,
            'total_lines': len(lines),
            'size': log_files[filename]['size'],
            'lines_requested': lines_to_show,
            'content': ''.join(lines[-lines_to_show:]) if lines else 'No hay datos',
            'timestamp': str(__import__('datetime').datetime.now()),
        })
    
    except Exception as e:
        logger.error(f"Error al obtener contenido de log: {str(e)}")
        return JsonResponse({
            'error': 'Error al obtener contenido',
            'detalle': str(e)
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def clear_log_file(request, filename):
    """Limpia un archivo de log específico"""
    if not request.user.is_staff:
        return JsonResponse({
            'error': 'Acceso denegado',
            'detalle': 'Solo los administradores pueden limpiar logs'
        }, status=403)
    
    try:
        log_files = get_log_files()
        
        if filename not in log_files:
            return JsonResponse({
                'error': 'Archivo de log no encontrado'
            }, status=404)
        
        file_path = log_files[filename]['path']
        
        # Limpiar el archivo (mantener el encabezado)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"[LOGS CLEARED] {__import__('datetime').datetime.now()}\n")
        
        logger.info(f"Log file '{filename}' cleared by {request.user.username}")
        
        return JsonResponse({
            'message': f'Archivo {filename} limpiado correctamente',
            'timestamp': str(__import__('datetime').datetime.now()),
        })
    
    except Exception as e:
        logger.error(f"Error al limpiar log: {str(e)}")
        return JsonResponse({
            'error': 'Error al limpiar log',
            'detalle': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def logs_api_stats(request):
    """Estadísticas de los logs de APIs"""
    if not request.user.is_staff:
        return JsonResponse({
            'error': 'Acceso denegado',
            'detalle': 'Solo los administradores pueden ver estadísticas'
        }, status=403)
    
    try:
        log_files = get_log_files()
        
        stats = {
            'total_log_files': len(log_files),
            'total_size_kb': sum(info['size_bytes'] for info in log_files.values()) / 1024,
            'files': {}
        }
        
        # Estadísticas por archivo
        for filename, info in log_files.items():
            stats['files'][filename] = {
                'size_kb': info['size_bytes'] / 1024,
                'size_mb': info['size_bytes'] / (1024 * 1024),
                'path': info['path'],
            }
            
            # Contar eventos por tipo
            try:
                with open(info['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    stats['files'][filename]['stats'] = {
                        'api_requests': content.count('API REQUEST'),
                        'api_responses': content.count('API RESPONSE'),
                        'api_errors': content.count('API ERROR'),
                        'db_operations': content.count('DB OPERATION'),
                        'login_attempts': content.count('LOGIN'),
                        'errors': content.count('ERROR'),
                        'warnings': content.count('WARNING'),
                    }
            except:
                stats['files'][filename]['stats'] = {'error': 'No se pudo leer'}
        
        return JsonResponse({
            'stats': stats,
            'timestamp': str(__import__('datetime').datetime.now()),
        })
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        return JsonResponse({
            'error': 'Error al obtener estadísticas',
            'detalle': str(e)
        }, status=500)
