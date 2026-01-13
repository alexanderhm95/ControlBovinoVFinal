"""
Módulo centralizado de logging para el Sistema de Control Bovino
Proporciona funciones de logging para APIs, modelos y vistas
"""

import logging
import json
from datetime import datetime

# Obtener loggers específicos
logger = logging.getLogger('temp_car')
api_logger = logging.getLogger('temp_car.views')
db_logger = logging.getLogger('django.db.backends')
request_logger = logging.getLogger('django.request')

class APILogger:
    """Clase para logging de APIs REST"""
    
    @staticmethod
    def log_request(endpoint, method, user=None, data=None):
        """Registra una solicitud API"""
        log_msg = f"API REQUEST | {method} {endpoint}"
        if user and user.is_authenticated:
            log_msg += f" | User: {user.username}"
        if data:
            try:
                log_msg += f" | Data: {json.dumps(data, ensure_ascii=False)[:100]}"
            except:
                log_msg += f" | Data: {str(data)[:100]}"
        api_logger.info(log_msg)
    
    @staticmethod
    def log_response(endpoint, status_code, method="POST", response_data=None):
        """Registra una respuesta API"""
        log_msg = f"API RESPONSE | {method} {endpoint} | Status: {status_code}"
        if response_data:
            try:
                log_msg += f" | Data: {json.dumps(response_data, ensure_ascii=False)[:100]}"
            except:
                log_msg += f" | Data: {str(response_data)[:100]}"
        
        if status_code >= 400:
            api_logger.error(log_msg)
        else:
            api_logger.info(log_msg)
    
    @staticmethod
    def log_error(endpoint, error, status_code=500):
        """Registra un error en API"""
        api_logger.error(
            f"API ERROR | {endpoint} | Status: {status_code} | Error: {str(error)}"
        )
    
    @staticmethod
    def log_validation_error(endpoint, field, message):
        """Registra errores de validación"""
        api_logger.warning(
            f"API VALIDATION ERROR | {endpoint} | Field: {field} | {message}"
        )


class ViewLogger:
    """Clase para logging de vistas"""
    
    @staticmethod
    def log_view_access(view_name, user=None):
        """Registra acceso a una vista"""
        log_msg = f"VIEW ACCESS | {view_name}"
        if user and user.is_authenticated:
            log_msg += f" | User: {user.username}"
        logger.info(log_msg)
    
    @staticmethod
    def log_view_error(view_name, error):
        """Registra error en una vista"""
        logger.error(f"VIEW ERROR | {view_name} | Error: {str(error)}")


class DatabaseLogger:
    """Clase para logging de base de datos"""
    
    @staticmethod
    def log_query(model_name, operation, count=None):
        """Registra operaciones en base de datos"""
        log_msg = f"DB OPERATION | Model: {model_name} | Operation: {operation}"
        if count:
            log_msg += f" | Affected: {count}"
        db_logger.debug(log_msg)
    
    @staticmethod
    def log_db_error(model_name, error):
        """Registra error en base de datos"""
        db_logger.error(f"DB ERROR | Model: {model_name} | Error: {str(error)}")


class MonitoringLogger:
    """Clase para logging de monitoreo y alertas"""
    
    @staticmethod
    def log_monitoring_alert(bovino_name, collar_id, alert_type, value):
        """Registra alertas de monitoreo"""
        logger.warning(
            f"MONITORING ALERT | Bovino: {bovino_name} | "
            f"Collar: {collar_id} | Type: {alert_type} | Value: {value}"
        )
    
    @staticmethod
    def log_monitoring_success(bovino_name, collar_id, temp, pulse):
        """Registra monitoreo exitoso"""
        logger.info(
            f"MONITORING SUCCESS | Bovino: {bovino_name} | "
            f"Collar: {collar_id} | Temp: {temp}°C | Pulse: {pulse} bpm"
        )


class ArduinoLogger:
    """Clase para logging de datos del Arduino"""
    
    @staticmethod
    def log_arduino_data(collar_id, bovino_name, temp, pulse):
        """Registra datos recibidos del Arduino"""
        api_logger.info(
            f"ARDUINO DATA | Collar: {collar_id} | "
            f"Bovino: {bovino_name} | Temp: {temp}°C | Pulse: {pulse} bpm"
        )
    
    @staticmethod
    def log_arduino_error(error):
        """Registra error en lectura Arduino"""
        api_logger.error(f"ARDUINO ERROR | {str(error)}")
    
    @staticmethod
    def log_arduino_validation_error(data, missing_fields):
        """Registra error de validación Arduino"""
        api_logger.warning(
            f"ARDUINO VALIDATION ERROR | Missing fields: {missing_fields} | Data: {data}"
        )


class UserActivityLogger:
    """Clase para logging de actividad de usuarios"""
    
    @staticmethod
    def log_login(username, success=True):
        """Registra intento de login"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"LOGIN {status} | Username: {username}")
    
    @staticmethod
    def log_logout(username):
        """Registra logout"""
        logger.info(f"LOGOUT | Username: {username}")
    
    @staticmethod
    def log_user_action(username, action, object_name=None):
        """Registra acciones de usuario"""
        log_msg = f"USER ACTION | User: {username} | Action: {action}"
        if object_name:
            log_msg += f" | Object: {object_name}"
        logger.info(log_msg)
    
    @staticmethod
    def log_registration(username, email):
        """Registra nuevo registro"""
        logger.info(f"USER REGISTRATION | Username: {username} | Email: {email}")


# Función de conveniencia para obtener todos los loggers
def get_all_loggers():
    """Retorna diccionario con todos los loggers disponibles"""
    return {
        'api': APILogger,
        'view': ViewLogger,
        'database': DatabaseLogger,
        'monitoring': MonitoringLogger,
        'arduino': ArduinoLogger,
        'user': UserActivityLogger,
    }


# Función para mostrar archivos de log disponibles
def get_log_files():
    """Retorna lista de archivos de log disponibles"""
    import os
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    
    log_files = {}
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            if file.endswith('.log'):
                file_path = os.path.join(log_dir, file)
                file_size = os.path.getsize(file_path)
                log_files[file] = {
                    'path': file_path,
                    'size': f"{file_size / 1024:.2f} KB",
                    'size_bytes': file_size
                }
    
    return log_files
