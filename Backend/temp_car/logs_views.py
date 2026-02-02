"""
Vistas para visualizar y gestionar logs
Accesibles sin necesidad de login
"""

import os
import logging
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from pathlib import Path

logger = logging.getLogger('temp_car')


def get_log_files():
    """Obtiene lista de archivos de log disponibles"""
    logs_dir = Path('logs')
    
    if not logs_dir.exists():
        return {}
    
    log_files = {}
    for log_file in logs_dir.glob('*.log'):
        log_files[log_file.name] = {
            'path': str(log_file),
            'size': log_file.stat().st_size,
        }
    
    return log_files


@require_http_methods(["GET"])
def view_logs_dashboard(request):
    """Vista del dashboard de logs - acceso público"""
    
    try:
        log_files = get_log_files()
        
        # Leer contenido de cada archivo de log
        logs_content = {}
        for filename, info in log_files.items():
            try:
                with open(info['path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Mostrar las últimas 100 líneas
                    logs_content[filename] = {
                        'total_lines': len(lines),
                        'last_100_lines': lines[-100:] if lines else [],
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


@require_http_methods(["GET"])
def get_log_content(request, filename):
    """Obtiene contenido de un archivo de log específico"""
    
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
                'error': 'Archivo no encontrado',
                'path': file_path
            }, status=404)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return JsonResponse({
            'filename': filename,
            'content': content,
            'lines': len(content.split('\n')),
        })
    
    except Exception as e:
        logger.error(f"Error al obtener contenido de log: {str(e)}")
        return JsonResponse({
            'error': 'Error al obtener contenido',
            'detalle': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_log_file(request, filename):
    """Descarga un archivo de log específico"""
    
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
                'error': 'Archivo no encontrado',
                'path': file_path
            }, status=404)
        
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=filename
        )
    
    except Exception as e:
        logger.error(f"Error al descargar log: {str(e)}")
        return JsonResponse({
            'error': 'Error al descargar log',
            'detalle': str(e)
        }, status=500)


@require_http_methods(["POST"])
def clear_log_file(request, filename):
    """Limpia (vacía) un archivo de log específico"""
    
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
                'error': 'Archivo no encontrado',
                'path': file_path
            }, status=404)
        
        # Limpiar el archivo
        with open(file_path, 'w') as f:
            f.write('')
        
        return JsonResponse({
            'mensaje': f'Archivo {filename} limpiado correctamente',
            'filename': filename
        })
    
    except Exception as e:
        logger.error(f"Error al limpiar log: {str(e)}")
        return JsonResponse({
            'error': 'Error al limpiar log',
            'detalle': str(e)
        }, status=500)


@require_http_methods(["GET"])
def logs_api_stats(request):
    """Obtiene estadísticas de los logs"""
    
    try:
        log_files = get_log_files()
        
        stats = {
            'total_files': len(log_files),
            'files': {},
            'total_size': 0,
            'timestamp': str(__import__('datetime').datetime.now()),
        }
        
        for filename, info in log_files.items():
            try:
                with open(info['path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    stats['files'][filename] = {
                        'size': info['size'],
                        'lines': len(lines),
                        'size_mb': info['size'] / (1024 * 1024),
                    }
                    stats['total_size'] += info['size']
            except Exception as e:
                stats['files'][filename] = {
                    'error': str(e)
                }
        
        stats['total_size_mb'] = stats['total_size'] / (1024 * 1024)
        
        return JsonResponse(stats)
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        return JsonResponse({
            'error': 'Error al obtener estadísticas',
            'detalle': str(e)
        }, status=500)
