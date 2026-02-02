"""
Vista principal del sistema de Control Bovino
Gestiona monitoreo, reportes, PDF y API para aplicaciones móviles
"""

# Django core imports
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from django.utils import timezone
from django.urls import reverse

# REST Framework imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Third party imports
from xhtml2pdf import pisa

# Python standard library imports
import json
import random
from datetime import datetime, timedelta, time
from io import BytesIO
import pytz
# Local imports
from .forms import PersonalInfoForm
from .models import (
    Bovinos,
    ControlMonitoreo,
    Lectura,
    PersonalInfo,
    Pulsaciones,
    Temperatura
)
from .utils.monitorChecking import (
    checkingMorning,
    checkingAfternoon,
    checkingNight,
    checkHoursMorning,
    checkHoursAfternoon,
    checkHoursNight,
    checkDate
)

####################################
# FUNCIONES HELPER
####################################

def obtener_turno_actual():
    """
    Función helper para obtener el turno actual y sus rangos horarios
    
    Returns:
        dict: {
            'turno_actual': str ('morning', 'afternoon', 'evening', 'night'),
            'turno_display': str ('Mañana', 'Tarde', 'Noche', 'Madrugada'),
            'hora_inicio': int (hora de inicio del turno),
            'hora_fin': int (hora de fin del turno),
            'hora_actual': int (hora actual),
            'fecha_actual': date (fecha actual en America/Guayaquil)
        }
    """
    # Obtener hora actual en zona de Guayaquil
    tz = pytz.timezone('America/Guayaquil')
    ahora = timezone.now().astimezone(tz)
    hora_actual = ahora.hour
    fecha_actual = ahora.date()
    
    # Determinar turno actual basado en la hora
    if hora_actual >= 7 and hora_actual < 12:
        turno_actual = 'morning'
        turno_display = 'Mañana'
        hora_inicio = 7
        hora_fin = 12
    elif hora_actual >= 12 and hora_actual < 18:
        turno_actual = 'afternoon'
        turno_display = 'Tarde'
        hora_inicio = 12
        hora_fin = 18
    elif hora_actual >= 18 and hora_actual < 24:
        turno_actual = 'evening'
        turno_display = 'Noche'
        hora_inicio = 18
        hora_fin = 24
    else:  # 0-7
        turno_actual = 'night'
        turno_display = 'Madrugada'
        hora_inicio = 0
        hora_fin = 7
    
    return {
        'turno_actual': turno_actual,
        'turno_display': turno_display,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin,
        'hora_actual': hora_actual,
        'fecha_actual': fecha_actual
    }

####################################
# VISTAS DE PLATAFORMA WEB
####################################
def error_404_view(request, exception):
    """Maneja errores 404 personalizados"""
    return render(request, '404.html', status=404)


############################################
# DASHBOARD - MONITOREO ACTUAL
############################################

@login_required
def monitoreo_actual(request):
    """
    Vista principal del dashboard de monitoreo en tiempo real
    Muestra todos los collares activos y permite seleccionar uno específico
    """
    try:
        # Obtener solo bovinos activos
        collares = Bovinos.objects.filter(activo=True).order_by('nombre')
        
        # Obtener el primer collar activo si existe
        primer_collar = collares.first()
        
        context = {
            'collares': collares,
            'idCollar': primer_collar.idCollar if primer_collar else None,
            'total_collares': collares.count(),
        }
        return render(request, 'appMonitor/dashboard/monitor.html', context)
    except Exception as e:
        messages.error(request, f'Error al cargar el monitoreo: {str(e)}')
        return render(request, 'appMonitor/dashboard/monitor.html', {
            'collares': [],
            'idCollar': None,
            'total_collares': 0
        })

@login_required
def dashBoardData(request, id_collar=None):
    """
    API endpoint para obtener datos del dashboard de un bovino específico
    Retorna información del collar y los controles de monitoreo del turno actual
    
    Args:
        request: HttpRequest
        id_collar: ID del collar a consultar
        
    Returns:
        JsonResponse con collar_info y ultimos_registros del turno actual
    """
    # Validar parámetro requerido
    if id_collar is None:
        return JsonResponse({
            'error': 'Se requiere un id_collar',
            'detalle': 'Debe proporcionar el ID del collar a consultar'
        }, status=400)

    try:
        # Obtener bovino activo por ID de collar
        bovino = Bovinos.objects.get(idCollar=id_collar, activo=True)
    except Bovinos.DoesNotExist:
        return JsonResponse({
            'error': 'Collar no encontrado',
            'detalle': f'No existe un bovino activo con el collar ID {id_collar}'
        }, status=404)

    # Obtener turno actual usando función helper
    turno_info = obtener_turno_actual()
    turno_actual = turno_info['turno_actual']
    turno_display = turno_info['turno_display']
    hora_inicio = turno_info['hora_inicio']
    hora_fin = turno_info['hora_fin']
    fecha_actual = turno_info['fecha_actual']
    
    # Buscar controles del turno actual de hoy
    controles_turno_actual = (
        ControlMonitoreo.objects
        .filter(id_Lectura__id_Bovino=bovino, fecha_lectura=fecha_actual)
        .select_related(
            'id_Lectura',
            'id_Lectura__id_Temperatura', 
            'id_Lectura__id_Pulsaciones',
            'id_User'
        )
        .order_by('-hora_lectura')
    )
    
    # Filtrar por rango horario del turno
    controles_en_turno = []
    for control in controles_turno_actual:
        hora_control = control.hora_lectura.hour
        if turno_actual == 'night':
            if hora_control < 7:
                controles_en_turno.append(control)
        else:
            if hora_control >= hora_inicio and hora_control < hora_fin:
                controles_en_turno.append(control)
    
    # Usar datos del primer control del turno actual si existe
    if controles_en_turno:
        control_principal = controles_en_turno[0]
        collar_info = {
            'idCollar': bovino.idCollar,
            'nombre': bovino.nombre,
            'temperatura': control_principal.id_Lectura.temperatura_valor,
            'pulsaciones': control_principal.id_Lectura.pulsaciones_valor,
            'estado_salud': control_principal.id_Lectura.estado_salud,
            'temperatura_normal': control_principal.id_Lectura.temperatura_normal,
            'pulsaciones_normales': control_principal.id_Lectura.pulsaciones_normales,
            'fecha_registro': f"{control_principal.fecha_lectura.strftime('%Y-%m-%d')} {control_principal.hora_lectura.strftime('%H:%M:%S')}",
            'turno': turno_display,
        }
    else:
        # Si no hay control en el turno, usar la última lectura de Arduino
        lectura = bovino.lecturas.order_by('-fecha_lectura', '-hora_lectura').first()
        
        if not lectura:
            return JsonResponse({
                'error': 'No hay lecturas disponibles',
                'detalle': f'El bovino {bovino.nombre} no tiene lecturas registradas'
            }, status=404)
        
        collar_info = {
            'idCollar': bovino.idCollar,
            'nombre': bovino.nombre,
            'temperatura': lectura.temperatura_valor,
            'pulsaciones': lectura.pulsaciones_valor,
            'estado_salud': lectura.estado_salud,
            'temperatura_normal': lectura.temperatura_normal,
            'pulsaciones_normales': lectura.pulsaciones_normales,
            'fecha_registro': f"{lectura.fecha_lectura.strftime('%Y-%m-%d')} {lectura.hora_lectura.strftime('%H:%M:%S')}",
            'turno': turno_display,
        }

    # Construir lista de controles del turno actual
    registros = [
        {
            'id_control': control.id_Control,
            'temperatura': control.id_Lectura.temperatura_valor,
            'pulsaciones': control.id_Lectura.pulsaciones_valor,
            'estado_salud': control.id_Lectura.estado_salud,
            'fecha_control': f"{control.fecha_lectura.strftime('%Y-%m-%d')} {control.hora_lectura.strftime('%H:%M:%S')}",
            'observaciones': control.observaciones or 'Sin observaciones',
            'accion_tomada': control.accion_tomada or 'Sin acción',
            'registrado_por': control.id_User.get_full_name() if control.id_User else 'Sistema',
        }
        for control in controles_en_turno
    ]

    return JsonResponse({
        'collar_info': collar_info,
        'ultimos_registros': registros,
        'total_registros': len(registros),
        'turno_actual': turno_display
    }, status=200)


def ultimoRegistro(request, collar_id):
    """
    API endpoint que retorna el último registro de lectura de un bovino
    Usado por el dashboard para actualizar información en tiempo real
    
    Args:
        request: HttpRequest
        collar_id: ID del collar del bovino
        
    Returns:
        JsonResponse con datos del último registro
    """
    try:
        # Buscar bovino activo por ID de collar
        bovino = Bovinos.objects.filter(idCollar=collar_id, activo=True).first()
        
        if bovino is None:
            return JsonResponse({
                'error': 'Bovino no encontrado',
                'detalle': f'No existe un bovino activo con collar ID {collar_id}'
            }, status=404)

        # Obtener última lectura usando related_name
        datos = bovino.lecturas.order_by('-fecha_lectura', '-hora_lectura').first()
        
        if datos is None:
            return JsonResponse({
                'error': 'Sin lecturas',
                'detalle': f'El bovino {bovino.nombre} no tiene lecturas registradas'
            }, status=404)

        # Construir respuesta usando propiedades del modelo
        reporte = {
            'fecha_lectura': datos.fecha_lectura.strftime('%Y-%m-%d'),
            'hora_lectura': datos.hora_lectura.strftime('%H:%M:%S'),
            'temperatura': datos.temperatura_valor,
            'pulsaciones': datos.pulsaciones_valor,
            'nombre_vaca': bovino.nombre,
            'collar_id': bovino.idCollar,
            'estado_salud': datos.estado_salud,
            'temperatura_normal': datos.temperatura_normal,
            'pulsaciones_normales': datos.pulsaciones_normales,
        }

        return JsonResponse(reporte, status=200)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Error interno',
            'detalle': str(e)
        }, status=500)
@login_required
def reportes(request):
    """
    Vista de reportes con paginación y filtro por fecha
    Muestra historial de CONTROLES DE MONITOREO registrados
    
    Args:
        request: HttpRequest con parámetros page y fecha_busqueda opcionales
        
    Returns:
        Template con reportes paginados de controles
    """
    page = request.GET.get('page', 1)
    fecha_busqueda = request.GET.get('fecha_busqueda')
    fecha_busqueda_obj = None

    # Obtener CONTROLES de monitoreo con optimización de consultas
    reportes_list = (
        ControlMonitoreo.objects
        .select_related(
            'id_Lectura',
            'id_Lectura__id_Bovino',
            'id_Lectura__id_Temperatura',
            'id_Lectura__id_Pulsaciones',
            'id_User'  # Usuario que registró el control
        )
        .order_by('-fecha_lectura', '-hora_lectura')
    )

    # Aplicar filtro por fecha si se proporciona
    if fecha_busqueda:
        try:
            fecha_busqueda_obj = datetime.strptime(fecha_busqueda, '%Y-%m-%d').date()
            reportes_list = reportes_list.filter(fecha_lectura=fecha_busqueda_obj)
        except ValueError:
            messages.warning(request, 'Formato de fecha inválido. Use YYYY-MM-DD')

    # Configurar paginación
    paginator = Paginator(reportes_list, 10)
    
    try:
        reportes = paginator.page(page)
    except PageNotAnInteger:
        reportes = paginator.page(1)
    except EmptyPage:
        reportes = paginator.page(paginator.num_pages)

    context = {
        'reportes': reportes,
        'fecha_busqueda': fecha_busqueda or '',
        'total_reportes': paginator.count,
    }

    return render(request, 'appMonitor/dashboard/reports.html', context)

def reporte_pdf(request):
    fecha_busqueda = request.GET.get('fecha_busqueda')
    
    # Obtener CONTROLES de monitoreo (no lecturas)
    reportes = (
        ControlMonitoreo.objects
        .select_related(
            'id_Lectura',
            'id_Lectura__id_Bovino',
            'id_Lectura__id_Temperatura',
            'id_Lectura__id_Pulsaciones',
            'id_User'
        )
        .order_by('-fecha_lectura', '-hora_lectura')
    )

    if fecha_busqueda:
        try:
            fecha_busqueda_obj = datetime.strptime(fecha_busqueda, '%Y-%m-%d').date()
            reportes = reportes.filter(fecha_lectura=fecha_busqueda_obj)
        except ValueError:
            # Manejo de error si la fecha ingresada no es válida
            return HttpResponse("Fecha de búsqueda inválida.", status=400)

    context = {
        'reportes': reportes,
        'fecha_busqueda': fecha_busqueda.strftime('%Y-%m-%d') if fecha_busqueda else None,
    }

    # Construir tabla HTML manualmente
    table_rows = ""
    for reporte in reportes:
        table_rows += f"""
        <tr>
            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{reporte.id_Lectura.id_Bovino.idCollar}</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{reporte.id_Lectura.id_Bovino.nombre}</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{reporte.fecha_lectura.strftime('%d-%m-%Y')} {reporte.hora_lectura.strftime('%H:%M')}</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{reporte.id_Lectura.id_Temperatura.valor}°C</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{reporte.id_Lectura.id_Pulsaciones.valor} BPM</td>
        </tr>
        """

    table_html = f"""
    <table id="tablaReportes" style="width: 95%; margin: 20px auto; border-collapse: collapse;">
        <thead>
            <tr>
                <th style="padding: 8px; text-align: center; background-color: #72b4fc; border: 1px solid #ddd;">Collar</th>
                <th style="padding: 8px; text-align: center; background-color: #72b4fc; border: 1px solid #ddd;">Nombre</th>
                <th style="padding: 8px; text-align: center; background-color: #72b4fc; border: 1px solid #ddd;">Fecha y Hora</th>
                <th style="padding: 8px; text-align: center; background-color: #72b4fc; border: 1px solid #ddd;">Temperatura</th>
                <th style="padding: 8px; text-align: center; background-color: #72b4fc; border: 1px solid #ddd;">Pulsaciones</th>
            </tr>
        </thead>
        <tbody>
            {table_rows if table_rows else '<tr><td colspan="5" style="padding: 8px; text-align: center;">No hay reportes disponibles</td></tr>'}
        </tbody>
    </table>
    """

    pdf = render_to_pdf(table_html, context)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"reporte_monitoreos_{fecha_busqueda or datetime.now().strftime('%Y-%m-%d')}.pdf"
        content = f'attachment; filename="{filename}"'
        response['Content-Disposition'] = content
        return response

    return HttpResponse("Error al generar el PDF.", status=500)


def render_to_pdf(html_content, context_dict={}):
    header_html = """
<table style="width: 100%; border-collapse: collapse;">
    <tr>
        <td style="padding: 10px;">
            <img src="./temp_car/static/assets/img/logounl.png" alt="Left Logo" style="width: 195px; height: auto; margin-right: 10px;">
        </td>
        <td style="padding: 10px; vertical-align: top; text-align: right;">
            <img src="./temp_car/static/assets/img/logoComputacion.png" alt="Right Logo" style="width: 100px; height: auto; margin-left: 10px;">
        </td>
    </tr>
</table>
<div style="text-align: center; margin: 20px 0;">
    <h1 style="font-size: 24px; color: #333; margin: 0;">Reporte de Monitoreos al Ganado Bovino Lechero</h1>
</div>
"""

    full_html = header_html + html_content

    footer_html = """
<footer style="text-align: center; margin-top: 20px; background-color: #f8f8f8; padding: 10px;">
    <p style="font-size: 12px; color: #333; margin: 0;">© All rights reserved | Carrera de Ingeniería en Computación</p>
</footer>
"""

    full_html += footer_html

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(full_html.encode("ISO-8859-1")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


@login_required
def temperatura(request):
    """
    Vista de monitoreo de temperatura corporal
    Muestra historial de CONTROLES DE MONITOREO registrados
    SOLO DATOS DE APP MÓVIL (excluye Arduino)
    
    Args:
        request: HttpRequest con parámetro page opcional
        
    Returns:
        Template con datos de temperatura de controles
    """
    try:
        page = request.GET.get('page', 1)
        
        # Obtener CONTROLES de monitoreo (no lecturas) con app móvil
        reportes_list = (
            ControlMonitoreo.objects
            .filter(id_Lectura__fuente='app_movil')  # Solo datos de app móvil
            .select_related(
                'id_Lectura',
                'id_Lectura__id_Bovino',
                'id_Lectura__id_Temperatura',
                'id_Lectura__id_Pulsaciones',
                'id_User'
            )
            .order_by('-fecha_lectura', '-hora_lectura')
        )
        
        # Obtener solo bovinos activos
        collares = Bovinos.objects.filter(activo=True).order_by('nombre')

        paginator = Paginator(reportes_list, 10)
        reportes = paginator.get_page(page)

    except Exception as e:
        messages.error(request, f'Error al obtener datos de temperatura: {str(e)}')
        reportes = []
        collares = []

    context = {
        'reportes': reportes,
        'collares': collares,
        'total_collares': collares.count() if collares else 0,
    }
    
    return render(request, 'appMonitor/dashboard/temperature.html', context)


@login_required
def frecuencia(request):
    """
    Vista de monitoreo de frecuencia cardíaca (pulsaciones)
    Muestra historial de CONTROLES DE MONITOREO registrados
    SOLO DATOS DE APP MÓVIL (excluye Arduino)
    
    Args:
        request: HttpRequest con parámetro page opcional
        
    Returns:
        Template con datos de frecuencia cardíaca de controles
    """
    try:
        page = request.GET.get('page', 1)
        
        # Obtener CONTROLES de monitoreo (no lecturas) con app móvil
        reportes_list = (
            ControlMonitoreo.objects
            .filter(id_Lectura__fuente='app_movil')  # Solo datos de app móvil
            .select_related(
                'id_Lectura',
                'id_Lectura__id_Bovino',
                'id_Lectura__id_Temperatura',
                'id_Lectura__id_Pulsaciones',
                'id_User'
            )
            .order_by('-fecha_lectura', '-hora_lectura')
        )
        
        # Obtener solo bovinos activos
        collares = Bovinos.objects.filter(activo=True).order_by('nombre')

        paginator = Paginator(reportes_list, 10)
        reportes = paginator.page(page)

    except PageNotAnInteger:
        reportes = paginator.page(1)
    except EmptyPage:
        reportes = paginator.page(paginator.num_pages)
    except Exception as e:
        messages.error(request, f'Error al obtener datos de frecuencia: {str(e)}')
        reportes = []
        collares = []

    context = {
        'reportes': reportes,
        'collares': collares,
        'total_collares': collares.count() if collares else 0,
    }

    return render(request, 'appMonitor/dashboard/heartRate.html', context)

##########################################
# API REST - CONSUMIDA POR APP MÓVIL
##########################################

class LoginView1(APIView):
    """
    API endpoint para autenticación de usuarios desde app móvil
    
    POST /api/movil/login/
    Body: {"username": "email@example.com", "password": "password"}
    """
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            # Intentar obtener datos de JSON primero, luego de POST
            if request.content_type == 'application/json':
                import json
                body = json.loads(request.body)
                username = body.get('username')
                password = body.get('password')
            else:
                username = request.POST.get('username') or request.data.get('username')
                password = request.POST.get('password') or request.data.get('password')
            
            # Validar que se proporcionaron credenciales
            if not username or not password:
                return Response({
                    'detalle': 'Credenciales incompletas',
                    'error': 'Se requieren username y password'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Autenticar usuario
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Obtener información personal
                try:
                    personaInfo = PersonalInfo.objects.get(email=username)
                    
                    # Extraer primer nombre y apellido
                    primer_nombre = personaInfo.nombre.split(' ')[0] if personaInfo.nombre else ''
                    primer_apellido = personaInfo.apellido.split(' ')[0] if personaInfo.apellido else ''
                    
                    login(request, user)
                    
                    body = {
                        'username': username,
                        'Nombres': f'{primer_nombre} {primer_apellido}'.strip(),
                        'nombre_completo': personaInfo.nombre_completo,
                        'is_staff': user.is_staff,
                    }
                    
                    return Response({
                        'detalle': 'Inicio de sesión exitoso',
                        'data': body
                    }, status=status.HTTP_200_OK)
                    
                except PersonalInfo.DoesNotExist:
                    return Response({
                        'detalle': 'Usuario sin información personal',
                        'error': 'El usuario no tiene perfil asociado'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'detalle': 'Credenciales inválidas',
                    'error': 'Usuario o contraseña incorrectos'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'detalle': 'Error en el servidor',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def registrar_datos_sensores(request):
    """
    API endpoint para registrar un control de monitoreo de una lectura existente
    
    POST /api/movil/datos/
    Body: {
        "username": "user@example.com",
        "collar_id": 1,
        "lectura_id": 123,  # ID de la Lectura que se vio en el modal
        "observaciones": "Sin observaciones"
    }
    
    IMPORTANTE: La Lectura debe ser del día actual
    
    Returns:
        JsonResponse con confirmación de registro
    """
    print("\n" + "="*80)
    print("[SENSORES] Nueva petición de registro de control")
    print(f"[SENSORES] Método: {request.method}")
    print("="*80)
    
    if request.method != 'POST':
        print(f"[SENSORES] ❌ Método {request.method} no permitido")
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use POST para esta solicitud'
        }, status=405)
    
    # Obtener parámetros de JSON
    try:
        body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        print(f"[SENSORES] Body recibido: {body}")
        
        if not body:
            print("[SENSORES] ❌ Body vacío")
            return JsonResponse({
                'error': 'Body vacío',
                'detalle': 'El body no puede estar vacío'
            }, status=400)
        
        data = json.loads(body)
        print(f"[SENSORES] JSON parseado: {data}")
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"[SENSORES] ❌ Error parseando JSON: {str(e)}")
        return JsonResponse({
            'error': 'JSON inválido',
            'detalle': f'El body debe ser JSON válido: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f"[SENSORES] ❌ Error general: {str(e)}")
        return JsonResponse({
            'error': 'Error al procesar solicitud',
            'detalle': str(e)
        }, status=400)
    
    # Extraer parámetros
    username = data.get('username')
    collar_id = data.get('collar_id')
    lectura_id = data.get('lectura_id')  # ID de la Lectura a registrar
    observaciones = data.get('observaciones', '')
    
    print(f"[SENSORES] Parámetros extraídos:")
    print(f"  - username: {username}")
    print(f"  - collar_id: {collar_id}")
    print(f"  - lectura_id: {lectura_id}")
    print(f"  - observaciones: {observaciones}")
    
    # Validar parámetros requeridos
    if not all([username, collar_id, lectura_id]):
        print("[SENSORES] ❌ Parámetros incompletos")
        return JsonResponse({
            'error': 'Parámetros incompletos',
            'detalle': 'Se requieren username, collar_id y lectura_id'
        }, status=400)
    
    try:
        # Validar valores numéricos
        try:
            lectura_id = int(lectura_id)
            collar_id = int(collar_id)
        except ValueError:
            print("[SENSORES] ❌ Valores numéricos inválidos")
            return JsonResponse({
                'error': 'Valores inválidos',
                'detalle': 'collar_id y lectura_id deben ser números enteros'
            }, status=400)
        
        # Buscar la Lectura
        print(f"[SENSORES] Buscando lectura con ID={lectura_id}...")
        try:
            lectura = Lectura.objects.get(id_Lectura=lectura_id)
        except Lectura.DoesNotExist:
            print(f"[SENSORES] ❌ Lectura no encontrada")
            return JsonResponse({
                'error': 'Lectura no encontrada',
                'detalle': f'No existe lectura con ID {lectura_id}'
            }, status=404)
        
        # VALIDACIÓN CRÍTICA: La Lectura debe ser de HOY
        import pytz
        tz = pytz.timezone('America/Guayaquil')
        ahora = timezone.now().astimezone(tz)
        fecha_actual = ahora.date()
        
        if lectura.fecha_lectura != fecha_actual:
            print(f"[SENSORES] ❌ Lectura de {lectura.fecha_lectura}, se requiere lectura de {fecha_actual}")
            return JsonResponse({
                'error': 'Lectura desactualizada',
                'detalle': f'La lectura es de {lectura.fecha_lectura}. Solo se aceptan lecturas de hoy ({fecha_actual})'
            }, status=400)
        
        print(f"[SENSORES] ✓ Lectura encontrada: {lectura.id_Lectura} (Bovino: {lectura.id_Bovino.nombre})")
        
        # Verificar que el collar_id coincida
        if lectura.id_Bovino.idCollar != collar_id:
            print(f"[SENSORES] ❌ El collar_id ({collar_id}) no coincide con la lectura ({lectura.id_Bovino.idCollar})")
            return JsonResponse({
                'error': 'Collar no coincide',
                'detalle': f'La lectura pertenece al collar {lectura.id_Bovino.idCollar}, no al {collar_id}'
            }, status=400)
        
        # Buscar usuario por nombre completo o username
        print(f"[SENSORES] Buscando usuario: {username}...")
        user = User.objects.filter(username=username).first()
        
        # Si no encuentra por username, buscar por nombre completo (first_name last_name)
        if not user:
            nombre_partes = username.split(' ')
            if len(nombre_partes) == 2:
                first_name, last_name = nombre_partes
                user = User.objects.filter(
                    first_name__iexact=first_name,
                    last_name__iexact=last_name
                ).first()
                if user:
                    print(f"[SENSORES] ✓ Usuario encontrado por nombre: {user.first_name} {user.last_name}")
            
            if not user:
                print(f"[SENSORES] ❌ Usuario no encontrado")
                return JsonResponse({
                    'error': 'Usuario no encontrado',
                    'detalle': f'El usuario {username} no existe. Intenta con el email o nombre completo.'
                }, status=404)
        else:
            print(f"[SENSORES] ✓ Usuario encontrado por username: {user.username}")
        
        # Crear ControlMonitoreo (registrar la lectura existente)
        print(f"[SENSORES] Registrando control de monitoreo...")
        control = ControlMonitoreo.objects.create(
            id_Lectura=lectura,
            id_User=user,
            fecha_lectura=lectura.fecha_lectura,
            hora_lectura=lectura.hora_lectura,
            observaciones=observaciones
        )
        
        print(f"[SENSORES] ✓ Control de monitoreo creado: {control.id_Control}")
        print(f"[SENSORES] ✓ Lectura registrada: {lectura.id_Lectura}")
        print(f"[SENSORES] ✓ Bovino: {lectura.id_Bovino.nombre}")
        print(f"[SENSORES] ✓ Temperatura: {lectura.temperatura_valor}°C")
        print(f"[SENSORES] ✓ Pulsaciones: {lectura.pulsaciones_valor} bpm")
        print(f"[SENSORES] ✓ Estado: {lectura.estado_salud}")
        
        return JsonResponse({
            'exito': True,
            'mensaje': 'Control registrado correctamente',
            'control_id': control.id_Control,
            'lectura_id': lectura.id_Lectura,
            'bovino_nombre': lectura.id_Bovino.nombre,
            'temperatura': lectura.temperatura_valor,
            'pulsaciones': lectura.pulsaciones_valor,
            'estado_salud': lectura.estado_salud,
            'fecha_registro': f"{lectura.fecha_lectura.strftime('%Y-%m-%d')} {lectura.hora_lectura.strftime('%H:%M:%S')}"
        }, status=201)
        
    except Exception as e:
        print(f"[SENSORES] ❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': 'Error al registrar control',
            'detalle': str(e)
        }, status=500)

@csrf_exempt
def reporte_por_id(request):
    """
    API endpoint para registrar monitoreo de un bovino desde app móvil
    Valida horarios y registra el control si cumple condiciones
    
    POST /api/reporte/
    Body: {"sensor": "collar_id", "username": "user@example.com"}
    
    Returns:
        JsonResponse con datos del reporte y estado de registro
    """
    print("\n" + "="*80)
    print("[MÓVIL] Nueva petición de reporte recibida")
    print(f"[MÓVIL] Método: {request.method}")
    print(f"[MÓVIL] Headers: {dict(request.headers)}")
    print("="*80)
    
    if request.method != 'POST':
        print(f"[MÓVIL] ❌ Método {request.method} no permitido")
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use POST para esta solicitud'
        }, status=405)
    
    # Obtener parámetros de JSON (no POST form)
    try:
        body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        print(f"[MÓVIL] Body recibido: {body}")
        
        if not body:
            print("[MÓVIL] ❌ Body vacío")
            return JsonResponse({
                'error': 'Body vacío',
                'detalle': 'El body no puede estar vacío'
            }, status=400)
        data = json.loads(body)
        print(f"[MÓVIL] JSON parseado: {data}")
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"[MÓVIL] ❌ Error parseando JSON: {str(e)}")
        return JsonResponse({
            'error': 'JSON inválido',
            'detalle': f'El body debe ser JSON válido: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f"[MÓVIL] ❌ Error general: {str(e)}")
        return JsonResponse({
            'error': 'Error al procesar solicitud',
            'detalle': str(e)
        }, status=400)
    
    collar_id = data.get('sensor')
    username = data.get('username')
    
    print(f"[MÓVIL] Parámetros extraídos:")
    print(f"  - collar_id: {collar_id}")
    print(f"  - username: {username}")
    
    # Validar parámetros requeridos
    if not collar_id or not username:
        print("[MÓVIL] ❌ Parámetros incompletos")
        return JsonResponse({
            'error': 'Parámetros incompletos',
            'detalle': 'Se requieren sensor y username'
        }, status=400)
    
    try:
        # Buscar bovino activo
        print(f"[MÓVIL] Buscando bovino con collar_id={collar_id}...")
        bovino = Bovinos.objects.filter(idCollar=collar_id, activo=True).first()
        if not bovino:
            print(f"[MÓVIL] ❌ Bovino no encontrado")
            return JsonResponse({
                'error': 'Bovino no encontrado',
                'detalle': f'No existe bovino activo con collar {collar_id}'
            }, status=404)
        
        print(f"[MÓVIL] ✓ Bovino encontrado: {bovino.nombre}")
        
        # Buscar usuario
        print(f"[MÓVIL] Buscando usuario: {username}...")
        user = User.objects.filter(username=username).first()
        if not user:
            print(f"[MÓVIL] ❌ Usuario no encontrado")
            return JsonResponse({
                'error': 'Usuario no encontrado',
                'detalle': f'El usuario {username} no existe'
            }, status=404)
        
        # Obtener última lectura usando related_name
        dato = bovino.lecturas.order_by('-fecha_lectura', '-hora_lectura').first()
        
        if not dato:
            return JsonResponse({
                'error': 'Sin lecturas',
                'detalle': f'El bovino {bovino.nombre} no tiene lecturas registradas'
            }, status=404)
        
        # Formatear fecha y hora
        fecha_creacion = f"{dato.fecha_lectura.strftime('%Y-%m-%d')} {dato.hora_lectura.strftime('%H:%M:%S')}"
        registro = False
        mensaje_registro = 'No se registró - fuera de horario'

        print(f"[MÓVIL] ✓ Usuario encontrado: {user.username}")
        
        # Verificar condiciones para registro
        print(f"[MÓVIL] Verificando condiciones de registro...")
        print(f"[MÓVIL]   - Última lectura: {dato.fecha_lectura} {dato.hora_lectura}")
        print(f"[MÓVIL]   - Estado de salud: {dato.estado_salud}")
        
        # Validar que la lectura sea de hoy
        if not checkDate(dato.fecha_lectura):
            print(f"[MÓVIL] ⚠️ Lectura no es de hoy")
            mensaje_registro = 'Lectura no es de hoy'
        
        # Verificar turno de mañana (7:00 - 12:00)
        elif checkHoursMorning(dato.hora_lectura):
            if checkingMorning(bovino):
                print(f"[MÓVIL] ✓ Registrando en turno MAÑANA")
                ControlMonitoreo.objects.create(
                    id_Lectura=dato,
                    id_User=user,
                    fecha_lectura=dato.fecha_lectura,
                    hora_lectura=dato.hora_lectura
                )
                registro = True
                mensaje_registro = 'Registrado en turno de mañana'
            else:
                print(f"[MÓVIL] ⚠️ Ya registrado en turno MAÑANA")
                mensaje_registro = 'Ya registrado en turno de mañana'

        # Verificar turno de tarde (12:01 - 18:00)
        elif checkHoursAfternoon(dato.hora_lectura):
            if checkingAfternoon(bovino):
                print(f"[MÓVIL] ✓ Registrando en turno TARDE")
                ControlMonitoreo.objects.create(
                    id_Lectura=dato,
                    id_User=user,
                    fecha_lectura=dato.fecha_lectura,
                    hora_lectura=dato.hora_lectura
                )
                registro = True
                mensaje_registro = 'Registrado en turno de tarde'
            else:
                print(f"[MÓVIL] ⚠️ Ya registrado en turno TARDE")
                mensaje_registro = 'Ya registrado en turno de tarde'

        # Verificar turno de noche (18:01 - 23:59)
        elif checkHoursNight(dato.hora_lectura):
            if checkingNight(bovino):
                print(f"[MÓVIL] ✓ Registrando en turno NOCHE")
                ControlMonitoreo.objects.create(
                    id_Lectura=dato,
                    id_User=user,
                    fecha_lectura=dato.fecha_lectura,
                    hora_lectura=dato.hora_lectura
                )
                registro = True
                mensaje_registro = 'Registrado en turno de noche'
            else:
                print(f"[MÓVIL] ⚠️ Ya registrado en turno NOCHE")
                mensaje_registro = 'Ya registrado en turno de noche'
        else:
            print(f"[MÓVIL] ⚠️ Hora fuera de turnos permitidos")

        # Construir respuesta usando propiedades del modelo
        reporte = {
            'collar_id': bovino.idCollar,
            'nombre_vaca': bovino.nombre,
            'temperatura': dato.temperatura_valor,
            'pulsaciones': dato.pulsaciones_valor,
            'estado_salud': dato.estado_salud,
            'temperatura_normal': dato.temperatura_normal,
            'pulsaciones_normales': dato.pulsaciones_normales,
            'fecha_creacion': fecha_creacion,
            'registrado': registro,
            'mensaje': mensaje_registro,
        }
        
        print(f"[MÓVIL] ✅ Respuesta enviada: {reporte}")
        print("="*80 + "\n")
        return JsonResponse({'reporte': reporte}, status=200)
        
    except Exception as e:
        print(f"[MÓVIL] ❌ Error general: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[MÓVIL] Traceback: {traceback.format_exc()}")
        print("="*80 + "\n")
        return JsonResponse({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }, status=500)

@api_view(['GET'])
@csrf_exempt
def obtener_datos_collar(request, collar_id):
    """
    API endpoint GET para obtener datos de monitoreo de un bovino por collar ID
    
    GET /api/movil/datos/<collar_id>/
    
    Returns:
        JsonResponse con datos del último registro del bovino
    """
    # Obtenemos fecha actual de hoy en zona horaria de Guayaquil
    print("\n" + "="*80)
    print(f"[MÓVIL] Nueva petición de datos para collar_id={collar_id}")
    print(f"[MÓVIL] Método: {request.method}")
    print("="*80)
    
    # Obtener turno actual usando función helper
    turno_info = obtener_turno_actual()
    turno_actual = turno_info['turno_actual']
    turno_display = turno_info['turno_display']
    hora_inicio = turno_info['hora_inicio']
    hora_fin = turno_info['hora_fin']
    fecha_actual = turno_info['fecha_actual']
    hora_actual = turno_info['hora_actual']
    
    try:
        # Buscar bovino activo por collar_id
        bovino = Bovinos.objects.filter(idCollar=collar_id, activo=True).first()
        if not bovino:
            return JsonResponse({
                'error': 'Bovino no encontrado',
                'detalle': f'No existe un bovino activo con collar ID {collar_id}'
            }, status=404)
        print(f"[MÓVIL] ✓ Bovino encontrado: {bovino.nombre}")
        
        # Buscar lectura del turno actual
        lectura_existe = Lectura.objects.filter(
            id_Bovino=bovino,
            fecha_lectura=fecha_actual,
            hora_lectura__hour__gte=hora_inicio,
            hora_lectura__hour__lt=hora_fin
        )
        
        # Obtener último registro del turno actual
        ultimo_dato = lectura_existe.order_by('-hora_lectura').first()
        
        print(f"[MÓVIL] Último dato obtenido: {ultimo_dato}")
        
        if not ultimo_dato:
            return JsonResponse({
                'error': 'Sin datos',
                'detalle': f'No hay registros para el bovino con collar {collar_id}'
            }, status=404)
        
        # Obtener hora actual en zona de Guayaquil
        tz = pytz.timezone('America/Guayaquil')
        ahora = timezone.now().astimezone(tz)
        print(f"[MÓVIL] Hora actual: {ahora.time()}")
        
        # Construir respuesta
        datos = {
            'collar_id': bovino.idCollar,
            'nombre': bovino.nombre,
            'ultimo_registro': {
                'id': ultimo_dato.id_Lectura,
                'temperatura': ultimo_dato.temperatura_valor,
                'pulsaciones': ultimo_dato.pulsaciones_valor,
                'estado_salud': ultimo_dato.estado_salud,
                'temperatura_normal': ultimo_dato.temperatura_normal,
                'pulsaciones_normales': ultimo_dato.pulsaciones_normales,
                'fecha': f"{ultimo_dato.fecha_lectura} {ultimo_dato.hora_lectura}"
            }
        }
        
        return JsonResponse({'datos': datos}, status=200)
        
    except Exception as e:
        print(f"[MÓVIL] ❌ Error: {str(e)}")
        return JsonResponse({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }, status=500)

@csrf_exempt
def verificar_lectura_turno(request, collar_id):
    """
    API endpoint GET para verificar si ya existe lectura registrada en el turno actual
    
    GET /api/movil/verificar-lectura/<collar_id>/
    
    Returns:
        JsonResponse con estado de lectura del turno
    """
    import pytz
    
    # Obtenemos fecha y hora actual en zona horaria de Guayaquil
    print("\n" + "="*80)
    print(f"[VERIFICAR] Nueva petición de verificación para collar_id={collar_id}")
    print(f"[VERIFICAR] Método: {request.method}")
    print("="*80)
    
    try:
        # Buscar bovino activo
        bovino = Bovinos.objects.filter(idCollar=collar_id, activo=True).first()
        if not bovino:
            return JsonResponse({
                'error': 'Bovino no encontrado',
                'detalle': f'No existe bovino activo con collar {collar_id}'
            }, status=404)
        
        # Obtener turno actual usando función helper
        turno_info = obtener_turno_actual()
        turno_actual = turno_info['turno_actual']
        turno_display = turno_info['turno_display']
        hora_inicio = turno_info['hora_inicio']
        hora_fin = turno_info['hora_fin']
        fecha_actual = turno_info['fecha_actual']
        hora_actual = turno_info['hora_actual']
        
        # Obtener hora actual completa para logging
        tz = pytz.timezone('America/Guayaquil')
        ahora = timezone.now().astimezone(tz)
        print(f"[VERIFICAR] Hora actual: {ahora.time()}")
        
        print(f"[VERIFICAR] Turno actual: {turno_display} ({hora_inicio}:00 - {hora_fin}:00)")
        # Buscar CONTROLES DE MONITOREO (app móvil) en el rango horario del turno actual
        try:
            # Buscar si hay algún CONTROL DE MONITOREO (no lectura de Arduino)
            control_existe = ControlMonitoreo.objects.filter(
                id_Lectura__id_Bovino=bovino,
                fecha_lectura=fecha_actual,
                hora_lectura__hour__gte=hora_inicio,
                hora_lectura__hour__lt=hora_fin
            )
            lectura_en_turno = control_existe.count() > 0
        except Exception as e:
            print(f"[VERIFICAR] Error verificando control por turno: {str(e)}")
            lectura_en_turno = False
        
        print(f"[VERIFICAR] Collar {collar_id} - Turno: {turno_display} - Lectura en turno: {lectura_en_turno}")
        
        # Construir respuesta
        respuesta = {
            'collar_id': bovino.idCollar,
            'bovino_nombre': bovino.nombre,
            'turno_actual': turno_actual,
            'turno_display': turno_display,
            'fecha_actual': fecha_actual.strftime('%Y-%m-%d'),
            'hora_actual': ahora.strftime('%H:%M:%S'),
            'lectura_registrada': lectura_en_turno,
            'bloqueado': lectura_en_turno  # Bloquea si ya hay lectura EN ESTE TURNO
        }
        
        # Obtener el último registro del bovino en el turno actual (para temperatura y pulsaciones)
        try:
            ultimo_registro = ControlMonitoreo.objects.filter(
                id_Lectura__id_Bovino=bovino,
                fecha_lectura=fecha_actual,
                hora_lectura__hour__gte=hora_inicio,
                hora_lectura__hour__lt=hora_fin
            ).order_by('-fecha_lectura', '-hora_lectura').first()
            if ultimo_registro:
                respuesta['temperatura'] = ultimo_registro.id_Lectura.temperatura_valor
                respuesta['pulsaciones'] = ultimo_registro.id_Lectura.pulsaciones_valor
                respuesta['estado_salud'] = ultimo_registro.id_Lectura.estado_salud
                respuesta['fecha_registro'] = f"{ultimo_registro.fecha_lectura} {ultimo_registro.hora_lectura}"
        except Exception as e:
            print(f"[VERIFICAR] Error obteniendo último registro: {str(e)}")
        
        return JsonResponse(respuesta, status=200)
        
    except Exception as e:
        print(f"[VERIFICAR] Error general: {str(e)}")
        return JsonResponse({
            'error': 'Error al verificar lectura',
            'detalle': str(e)
        }, status=500)


#########################################

##########################################
# API - CONSUMIDA POR DISPOSITIVO IoT (ARDUINO)
##########################################

@csrf_exempt
@api_view(['POST'])
def lecturaDatosArduino(request):
    """
    API endpoint para recibir datos del dispositivo Arduino/ESP32
    Crea o actualiza bovino y registra lectura de sensores
    
    POST /api/arduino/monitoreo
    Headers:
        Content-Type: application/json
        Authorization: Bearer sk_arduino_controlbovino_2024 (OBLIGATORIO)
    
    Body (JSON): {
        "collar_id": int,
        "nombre_vaca": str,
        "mac_collar": str,
        "temperatura": int,
        "pulsaciones": int (opcional, se genera aleatoriamente si no se proporciona)
    }
    
    Returns:
        JsonResponse con estado de guardado (201 Created, 400 Bad Request, 401 Unauthorized, 500 Error)
    """
    print("\n" + "="*80)
    print("[ARDUINO] Nueva petición recibida")
    print(f"[ARDUINO] Método: {request.method}")
    print("="*80)
    
    try:
        # VALIDACIÓN OBLIGATORIA DE AUTENTICACIÓN
        api_key_valida = 'sk_arduino_controlbovino_2024'
        auth_header = request.headers.get('Authorization', '')
                
        if not auth_header:
            print(f"[ARDUINO] ❌ Authorization header faltante")
            return JsonResponse({
                'error': 'No autorizado',
                'detalle': 'Header Authorization requerido. Use: Authorization: Bearer sk_arduino_controlbovino_2024'
            }, status=401)
        
        # Validar formato Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            print(f"[ARDUINO] ❌ Formato Authorization inválido")
            return JsonResponse({
                'error': 'No autorizado',
                'detalle': 'Formato Authorization inválido. Use: Bearer YOUR_API_KEY'
            }, status=401)
        
        api_key_recibida = parts[1]
        
        # Validar clave
        if api_key_recibida != api_key_valida:
            print(f"[ARDUINO] ❌ API Key inválida: {api_key_recibida[:10]}...")
            return JsonResponse({
                'error': 'No autorizado',
                'detalle': 'API Key inválida'
            }, status=401)
        
        print(f"[ARDUINO] ✅ Autenticación exitosa")
        
        # Decodificar JSON del body
        body_text = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        lecturaDecoded = json.loads(body_text)
        
        if lecturaDecoded.get('collar_id') is None or lecturaDecoded.get('temperatura') is None :
            print(f"[ARDUINO] ❌ Parámetros requeridos faltantes")
            return JsonResponse({
                'error': 'Parámetros incompletos',
                'detalle': 'Se requieren collar_id y temperatura en el body'
            }, status=400)
        
        
        # Extraer datos del JSON
        collar_id = lecturaDecoded.get('collar_id')
        Bovino = Bovinos.objects.filter(idCollar=collar_id).first()
        if not Bovino:
            Bovino = Bovinos()
            Bovino.idCollar = lecturaDecoded.get('collar_id')
            Bovino.nombre = lecturaDecoded.get('nombre_vaca')
            Bovino.macCollar = lecturaDecoded.get('mac_collar')
            # Asignar fecha de registro y activo con America/Guayaquil
            import pytz
            tz = pytz.timezone('America/Guayaquil')
            ahora = timezone.now().astimezone(tz)
            Bovino.fecha_registro = ahora.date()
            Bovino.activo = True
        else:
            Bovino.macCollar = lecturaDecoded.get('mac_collar')
        Bovino.save()
        
        
        # Si no se envía pulsaciones, generar  pulsaciones de acuerdo al valor de temperatura (Se debe tener en cuenta que es para bovinos adultos en especial para vacas lecheras)
        pulsaciones = lecturaDecoded.get('pulsaciones')
        
        if pulsaciones is None:
            temperatura_val = lecturaDecoded.get('temperatura')
            if temperatura_val is not None:
                try:
                    temperatura_int = int(temperatura_val)
                    
                    # RANGO FISIOLÓGICO PARA BOVINOS LECHEROS ADULTOS: Temp 38-39°C, Pulsaciones: 50-65 BPM
                    if temperatura_int < 36:
                        # Hipotermia - pulsaciones muy bajas
                        pulsaciones = 35  # Bradicardia
                        print(f"[ARDUINO] ⚠️ Hipotermia ({temperatura_int}°C) - pulsaciones bajas: {pulsaciones}")
                    elif 36 <= temperatura_int < 38:
                        # Temperatura baja - pulsaciones bajas
                        pulsaciones = 40 + (temperatura_int - 36) * 5  # Rango 40-50 BPM
                        print(f"[ARDUINO] Generando pulsaciones para temperatura baja: {pulsaciones}")
                    elif 38 <= temperatura_int <= 39:
                        # Rango normal para bovinos - pulsaciones normales
                        pulsaciones = 50 + (temperatura_int - 38) * 10  # Rango 50-65 BPM
                        print(f"[ARDUINO] Generando pulsaciones para temperatura normal (bovino): {pulsaciones}")
                    elif 39 < temperatura_int <= 40:
                        # Fiebre leve - pulsaciones elevadas
                        pulsaciones = 65 + (temperatura_int - 39) * 20  # Rango 65-85 BPM
                        print(f"[ARDUINO] Generando pulsaciones para fiebre leve: {pulsaciones}")
                    else:
                        # Fiebre alta (>40°C) - pulsaciones muy elevadas
                        pulsaciones = 85 + (temperatura_int - 40) * 15  # Rango 85+
                        print(f"[ARDUINO] Generando pulsaciones para fiebre alta: {pulsaciones}")
                    
                    pulsaciones = int(pulsaciones)  # Asegurar que sea entero
                    
                except (ValueError, TypeError):
                    pulsaciones = 60  # Valor por defecto si hay error de conversión
                    print(f"[ARDUINO] Error al procesar temperatura, asignando pulsaciones por defecto: {pulsaciones}")
            else:
                pulsaciones = 60  # Valor por defecto si no hay temperatura
                print(f"[ARDUINO] Temperatura no proporcionada, asignando pulsaciones por defecto: {pulsaciones}")
        else:
            # Si se recibieron pulsaciones, convertirlas a entero
            try:
                pulsaciones = int(pulsaciones)
                print(f"[ARDUINO] Pulsaciones recibidas del Arduino: {pulsaciones}")
            except (ValueError, TypeError):
                pulsaciones = 60
                print(f"[ARDUINO] Error convertiendo pulsaciones, asignando valor por defecto: {pulsaciones}")

        # Validar que todos los datos requeridos estén presentes
        print(f"[ARDUINO] Datos extraídos:")
        print(f"  - collar_id: {collar_id}")
        print(f"  - nombre_vaca: {Bovino.nombre}")
        print(f"  - mac_collar: {Bovino.macCollar}")
        print(f"  - temperatura: {int(lecturaDecoded.get('temperatura'))}")
        print(f"  - pulsaciones: {pulsaciones}")
        
        # Crear registros de temperatura y pulsaciones
        print(f"[ARDUINO] Creando registros de sensores...")
        temperatura_obj = Temperatura.objects.create(valor=int(lecturaDecoded.get('temperatura')))
        pulsaciones_obj = Pulsaciones.objects.create(valor=pulsaciones)
        print(f"[ARDUINO] Temperatura ID: {temperatura_obj.id_Temperatura}, Pulsaciones ID: {pulsaciones_obj.id_Pulsaciones}")
        
        # Crear lectura
        import pytz
        tz = pytz.timezone('America/Guayaquil')
        ahora = timezone.now().astimezone(tz)
        
        lectura = Lectura.objects.create(
            id_Temperatura=temperatura_obj,
            id_Pulsaciones=pulsaciones_obj,
            id_Bovino=Bovino,
            fecha_lectura=ahora.date(),
            hora_lectura=ahora.time(),
            fuente='arduino'  # Marca como proveniente del Arduino
        )
        print(f"[ARDUINO] Lectura creada ID: {lectura.id_Lectura}")
        print(f"[ARDUINO] Estado de salud: {lectura.estado_salud}")
        
        respuesta = {
            'mensaje': 'Datos guardados exitosamente',
            'data': {
                'lectura_id': lectura.id_Lectura,
                'bovino': Bovino.nombre,
                'collar_id': Bovino.idCollar,
                'temperatura': int(lecturaDecoded.get('temperatura')),
                'pulsaciones': pulsaciones,
                'estado_salud': lectura.estado_salud,
                'bovino_nuevo': Bovino.fecha_registro == ahora.date(),
                'timestamp': lectura.fecha_lectura.isoformat()
            }
        }
        print(f"[ARDUINO] ✅ Respuesta enviada: {respuesta}")
        print("="*80 + "\n")
        return JsonResponse(respuesta, status=201)
        
    except json.JSONDecodeError as e:
        print(f"[ARDUINO] ❌ Error JSON: {str(e)}")
        print("="*80 + "\n")
        return JsonResponse({
            'error': 'JSON inválido',
            'detalle': 'El body no es un JSON válido'
        }, status=400)
    except Exception as e:
        print(f"[ARDUINO] ❌ Error general: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[ARDUINO] Traceback: {traceback.format_exc()}")
        print("="*80 + "\n")
        return JsonResponse({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }, status=500)
        
    except json.JSONDecodeError as e:
        print(f"[ARDUINO] ❌ Error JSON: {str(e)}")
        print("="*80 + "\n")
        return JsonResponse({
            'error': 'JSON inválido',
            'detalle': 'El body no es un JSON válido'
        }, status=400)
    except Exception as e:
        print(f"[ARDUINO] ❌ Error general: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[ARDUINO] Traceback: {traceback.format_exc()}")
        print("="*80 + "\n")
        return JsonResponse({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }, status=500)


# ============================================================================
# API: CONTROLES MANUALES - 3 lecturas por día (morning/afternoon/evening)
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def controlMonitoreoRegistro(request):
    """
    GET: Obtiene los controles de monitoreo registrados
    
    Headers requeridos:
    - Authorization: Bearer {token}
    
    Parámetros opcionales:
    - fecha: fecha del control (formato YYYY-MM-DD, default: hoy)
    - collar_id: filtrar por ID de collar
    """
    print("\n" + "="*80)
    print("[CONTROL_MONITOREO] Iniciando solicitud GET")
    print(f"[CONTROL_MONITOREO] Usuario: {request.user}")
    print("="*80 + "\n")
    
    # Validar autenticación
    if not request.user.is_authenticated:
        print("[CONTROL_MONITOREO] ❌ Usuario no autenticado")
        return JsonResponse({
            'error': 'No autorizado',
            'detalle': 'Autenticación requerida'
        }, status=401)
    
    try:
        from datetime import date
        from .serializers import ControlMonitoreoSerializer
        
        # Parámetros opcionales
        fecha_control = request.GET.get('fecha', str(date.today()))
        collar_id = request.GET.get('collar_id', None)
        
        print(f"[CONTROL_MONITOREO] Filtros: fecha={fecha_control}, collar_id={collar_id}")
        
        # Construir queryset
        queryset = ControlMonitoreo.objects.filter(
            fecha_lectura=fecha_control
        ).select_related(
            'id_Lectura',
            'id_Lectura__id_Bovino',
            'id_User'
        )
        
        if collar_id:
            queryset = queryset.filter(id_Lectura__id_Bovino__idCollar=collar_id)
        
        serializer = ControlMonitoreoSerializer(queryset, many=True)
        
        print(f"[CONTROL_MONITOREO] ✅ {len(serializer.data)} controles encontrados")
        
        return JsonResponse({
            'total': len(serializer.data),
            'fecha': fecha_control,
            'controles': serializer.data
        }, status=200)
    
    except Exception as e:
        print(f"[CONTROL_MONITOREO] ❌ Error: {str(e)}")
        return JsonResponse({
            'error': 'Error al obtener controles',
            'detalle': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def controlMonitoreoDetalle(request, control_id):
    """
    PUT: Actualiza un control de monitoreo existente
    DELETE: Elimina un control de monitoreo
    
    Solo el usuario que creó el control puede modificarlo
    """
    print("\n" + "="*80)
    print(f"[CONTROL_MONITOREO_DETALLE] Operación sobre control ID: {control_id}")
    print(f"[CONTROL_MONITOREO_DETALLE] Método: {request.method}")
    print("="*80 + "\n")
    
    # Validar autenticación
    if not request.user.is_authenticated:
        print("[CONTROL_MONITOREO_DETALLE] ❌ Usuario no autenticado")
        return JsonResponse({
            'error': 'No autorizado',
            'detalle': 'Autenticación requerida'
        }, status=401)
    
    try:
        control = ControlMonitoreo.objects.get(id_Control=control_id)
    except ControlMonitoreo.DoesNotExist:
        print(f"[CONTROL_MONITOREO_DETALLE] ❌ Control no encontrado: {control_id}")
        return JsonResponse({
            'error': 'No encontrado',
            'detalle': f'Control {control_id} no existe'
        }, status=404)
    
    # Verificar permisos (solo el usuario que creó puede modificar)
    if control.id_User != request.user:
        print(f"[CONTROL_MONITOREO_DETALLE] ❌ Acceso denegado - Usuario: {request.user}, Creador: {control.id_User}")
        return JsonResponse({
            'error': 'Acceso denegado',
            'detalle': 'Solo el usuario que creó el control puede modificarlo'
        }, status=403)
    
    if request.method == 'PUT':
        try:
            from .serializers import ControlMonitoreoSerializer
            
            body_text = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            datos = json.loads(body_text)
            
            print(f"[CONTROL_MONITOREO_DETALLE] Datos para actualización: {datos}")
            
            # Actualizar campos permitidos
            if 'observaciones' in datos:
                control.observaciones = datos['observaciones']
            if 'accion_tomada' in datos:
                control.accion_tomada = datos['accion_tomada']
            
            control.save()
            
            print(f"[CONTROL_MONITOREO_DETALLE] ✅ Control actualizado")
            
            serializer = ControlMonitoreoSerializer(control)
            return JsonResponse({
                'id': control.id_Control,
                'estado': 'actualizado',
                'data': serializer.data
            }, status=200)
        
        except Exception as e:
            print(f"[CONTROL_MONITOREO_DETALLE] ❌ Error: {str(e)}")
            return JsonResponse({
                'error': 'Error al actualizar control',
                'detalle': str(e)
            }, status=500)
    
    elif request.method == 'DELETE':
        try:
            bovino_nombre = control.id_Lectura.id_Bovino.nombre
            control.delete()
            
            print(f"[CONTROL_MONITOREO_DETALLE] ✅ Control eliminado para {bovino_nombre}")
            
            return JsonResponse({
                'estado': 'eliminado',
                'mensaje': f'Control de {bovino_nombre} eliminado exitosamente'
            }, status=200)
        
        except Exception as e:
            print(f"[CONTROL_MONITOREO_DETALLE] ❌ Error al eliminar: {str(e)}")
            return JsonResponse({
                'error': 'Error al eliminar control',
                'detalle': str(e)
            }, status=500)


