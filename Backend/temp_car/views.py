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
    checkHoursMorning,
    checkHoursAfternoon,
    checkDate
)

####################################
# VISTAS DE PLATAFORMA WEB
####################################

def prueba(request):
    """Vista de prueba para desarrollo"""
    return render(request, 'appMonitor/dashboard/temperature.html')


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

def dashBoardData(request, id_collar=None):
    """
    API endpoint para obtener datos del dashboard de un bovino específico
    Retorna información del collar y las últimas 10 lecturas monitoreadas
    
    Args:
        request: HttpRequest
        id_collar: ID del collar a consultar
        
    Returns:
        JsonResponse con collar_info y ultimos_registros
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

    # Obtener última lectura usando related_name
    lectura = bovino.lecturas.order_by('-fecha_lectura', '-hora_lectura').first()
    
    if not lectura:
        return JsonResponse({
            'error': 'No hay lecturas disponibles',
            'detalle': f'El bovino {bovino.nombre} no tiene lecturas registradas'
        }, status=404)

    # Usar propiedades del modelo mejorado
    collar_info = {
        'idCollar': bovino.idCollar,
        'nombre': bovino.nombre,
        'temperatura': lectura.temperatura_valor,
        'pulsaciones': lectura.pulsaciones_valor,
        'estado_salud': lectura.estado_salud,
        'temperatura_normal': lectura.temperatura_normal,
        'pulsaciones_normales': lectura.pulsaciones_normales,
        'fecha_registro': f"{lectura.fecha_lectura.strftime('%Y-%m-%d')} {lectura.hora_lectura.strftime('%H:%M:%S')}",
    }

    # Obtener últimas 10 lecturas monitoreadas usando select_related para optimización
    ultimas_lecturas = (
        ControlMonitoreo.objects
        .filter(id_Lectura__id_Bovino=bovino)
        .select_related('id_Lectura__id_Temperatura', 'id_Lectura__id_Pulsaciones')
        .order_by('-fecha_lectura', '-hora_lectura')[:10]
    )

    # Construir lista de registros
    registros = [
        {
            'temperatura': control.id_Lectura.temperatura_valor,
            'pulsaciones': control.id_Lectura.pulsaciones_valor,
            'estado_salud': control.id_Lectura.estado_salud,
            'fecha_registro': f"{control.fecha_lectura.strftime('%Y-%m-%d')} {control.hora_lectura.strftime('%H:%M:%S')}",
            'observaciones': control.observaciones or '',
            'accion_tomada': control.accion_tomada or '',
        }
        for control in ultimas_lecturas
    ]

    return JsonResponse({
        'collar_info': collar_info,
        'ultimos_registros': registros,
        'total_registros': len(registros)
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
    Muestra historial de lecturas con opción de búsqueda por fecha
    
    Args:
        request: HttpRequest con parámetros page y fecha_busqueda opcionales
        
    Returns:
        Template con reportes paginados
    """
    page = request.GET.get('page', 1)
    fecha_busqueda = request.GET.get('fecha_busqueda')
    fecha_busqueda_obj = None

    # Obtener lecturas con optimización de consultas
    reportes_list = (
        Lectura.objects
        .select_related('id_Bovino', 'id_Temperatura', 'id_Pulsaciones')
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
    reportes = Lectura.objects.all()

    if fecha_busqueda:
        try:
            fecha_busqueda = datetime.strptime(fecha_busqueda, '%Y-%m-%d').date()
            reportes = reportes.filter(fecha_lectura__date=fecha_busqueda)
        except ValueError:
            # Manejo de error si la fecha ingresada no es válida
            return HttpResponse("Fecha de búsqueda inválida.", status=400)

    context = {
        'reportes': reportes,
        'fecha_busqueda': fecha_busqueda.strftime('%Y-%m-%d') if fecha_busqueda else None,
    }

    table_content = get_template('panel_tecnico_docente/reportes.html').render(context).split('<table id="tablaReportes">')[1].split('</table>')[0]
    table_content = table_content.replace('<th>', '<th style="padding: 8px; text-align: center; background-color: #72b4fc;">')
    table_content = table_content.replace('<td>', '<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">')
    table_html = f'<table id="tablaReportes" style="width: 80%; margin: 20px auto; border-collapse: collapse;">{table_content}</table>'

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
    Muestra historial de temperaturas con gráficos y análisis
    
    Args:
        request: HttpRequest con parámetro page opcional
        
    Returns:
        Template con datos de temperatura
    """
    try:
        page = request.GET.get('page', 1)
        
        # Optimizar consulta con select_related
        reportes_list = (
            Lectura.objects
            .select_related('id_Bovino', 'id_Temperatura', 'id_Pulsaciones')
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
    Muestra historial de pulsaciones con gráficos y análisis
    
    Args:
        request: HttpRequest con parámetro page opcional
        
    Returns:
        Template con datos de frecuencia cardíaca
    """
    try:
        page = request.GET.get('page', 1)
        
        # Optimizar consulta con select_related
        reportes_list = (
            Lectura.objects
            .select_related('id_Bovino', 'id_Temperatura', 'id_Pulsaciones')
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
    
    POST /api/login/
    Body: {"username": "email@example.com", "password": "password"}
    """
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
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
        
        # Verificar condiciones para registro de mañana
        print(f"[MÓVIL] Verificando condiciones de registro...")
        print(f"[MÓVIL]   - Última lectura: {dato.fecha_lectura} {dato.hora_lectura}")
        print(f"[MÓVIL]   - Estado de salud: {dato.estado_salud}")
        
        if (checkingMorning(bovino) and 
            checkHoursMorning(dato.hora_lectura) and 
            checkDate(dato.fecha_lectura)):
            
            print(f"[MÓVIL] ✓ Condiciones cumplidas para turno MAÑANA")
            ControlMonitoreo.objects.create(
                id_Lectura=dato,
                id_User=user,
            )
            registro = True
            mensaje_registro = 'Registrado en turno de mañana'

        # Verificar condiciones para registro de tarde
        elif (checkingAfternoon(bovino) and 
              checkHoursAfternoon(dato.hora_lectura) and 
              checkDate(dato.fecha_lectura)):
            
            print(f"[MÓVIL] ✓ Condiciones cumplidas para turno TARDE")
            ControlMonitoreo.objects.create(
                id_Lectura=dato,
                id_User=user,
            )
            registro = True
            mensaje_registro = 'Registrado en turno de tarde'
        else:
            print(f"[MÓVIL] ⚠️ No se cumplieron condiciones de registro")

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

@csrf_exempt
def obtener_datos_collar(request, collar_id):
    """
    API endpoint GET para obtener datos de monitoreo de un bovino por collar ID
    
    GET /api/movil/datos/<collar_id>/
    
    Returns:
        JsonResponse con datos del último registro del bovino
    """
    if request.method != 'GET':
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use GET para esta solicitud'
        }, status=405)
    
    try:
        # Buscar bovino activo por collar_id
        bovino = Bovinos.objects.filter(idCollar=collar_id, activo=True).first()
        
        if not bovino:
            return JsonResponse({
                'error': 'Bovino no encontrado',
                'detalle': f'No existe un bovino activo con collar ID {collar_id}'
            }, status=404)
        
        # Obtener último registro de monitoreo
        ultimo_dato = Lectura.objects.filter(id_Bovino=bovino).order_by('-id_Lectura').first()
        
        if not ultimo_dato:
            return JsonResponse({
                'error': 'Sin datos',
                'detalle': f'No hay registros para el bovino con collar {collar_id}'
            }, status=404)
        
        # Construir respuesta
        datos = {
            'collar_id': bovino.idCollar,
            'bovino_id': bovino.id_Bovinos,
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
        return JsonResponse({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }, status=500)

@csrf_exempt
def apiRegister(request):
    """
    API endpoint para registro de usuarios desde app móvil
    Crea usuario de Django y perfil PersonalInfo
    
    POST /api/register/
    Body: form data con cedula, telefono, nombre, apellido, email
    
    Returns:
        JsonResponse con estado de creación
    """
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use POST para registrar usuarios'
        }, status=405)
    
    # Obtener datos de JSON (no form data)
    try:
        body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        if not body:
            return JsonResponse({
                'error': 'Body vacío',
                'detalle': 'El body no puede estar vacío'
            }, status=400)
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({
            'error': 'JSON inválido',
            'detalle': f'El body debe ser JSON válido: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Error al procesar solicitud',
            'detalle': str(e)
        }, status=400)
    
    # Validar campos requeridos
    required_fields = ['username', 'email', 'cedula', 'telefono', 'nombre', 'apellido']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return JsonResponse({
            'error': 'Campos requeridos incompletos',
            'detalle': f'Se requieren: {", ".join(missing_fields)}'
        }, status=400)
    
    try:
        # Verificar si ya existe un usuario con ese email
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({
                'error': 'Email ya registrado',
                'detalle': 'Ya existe un usuario con este email'
            }, status=400)
        
        # Crear usuario de Django
        user = get_user_model().objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data.get('password', data['cedula']),  # Usar contraseña o cédula por defecto
            first_name=data['nombre'],
            last_name=data['apellido']
        )
        
        # Crear perfil PersonalInfo
        PersonalInfo.objects.create(
            email=data['email'],
            cedula=data['cedula'],
            telefono=data['telefono'],
            nombre=data['nombre'],
            apellido=data['apellido']
        )
        
        return JsonResponse({
            'message': 'Usuario creado exitosamente',
            'data': {
                'username': user.username,
                'email': user.email,
                'nombre': user.first_name,
                'apellido': user.last_name
            }
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Error al crear usuario',
            'detalle': str(e)
        }, status=500)

def apiList(request):
    """
    API endpoint para listar usuarios desde app móvil
    Excluye usuarios staff y retorna información de perfil
    
    GET /api/users/
    
    Returns:
        JsonResponse con diccionario de usuarios
    """
    try:
        # Obtener solo usuarios no-staff
        usuarios_list = User.objects.filter(is_staff=False)
        
        if not usuarios_list.exists():
            return JsonResponse({
                'error': 'Sin usuarios',
                'detalle': 'No hay usuarios no-staff registrados'
            }, status=404)
        
        usuarios = {}
        
        for user in usuarios_list:
            # Buscar perfil asociado
            profile = PersonalInfo.objects.filter(email=user.email).first()
            
            usuarios[user.id] = {
                'userId': user.id,
                'id': user.id,
                'nombre': user.first_name or "Sin nombre",
                'apellido': user.last_name or "Sin apellido",
                'nombre_completo': profile.nombre_completo if profile else f"{user.first_name} {user.last_name}",
                'email': user.email or "Sin email",
                'cedula': profile.cedula if profile else "Sin cédula",
                'telefono': profile.telefono if profile else "Sin teléfono",
                'activo': user.is_active,
                'is_staff': user.is_staff,
            }
        
        return JsonResponse({
            'usuarios': usuarios,
            'total': len(usuarios)
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Error al obtener usuarios',
            'detalle': str(e)
        }, status=500)

@csrf_exempt
def apiEdit(request, user_id):
    """
    API endpoint para editar usuario desde app móvil
    Actualiza tanto el User como el PersonalInfo
    
    POST/PUT/PATCH /api/editar/<user_id>/
    Body: form data o JSON con campos a actualizar
    
    GET: Retorna los datos actuales del usuario
    
    Returns:
        JsonResponse con estado de actualización
    """
    try:
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(PersonalInfo, email=user.email)
    except Exception as e:
        return JsonResponse({
            'error': 'Usuario no encontrado',
            'detalle': str(e)
        }, status=404)

    # Permitir GET para obtener datos del usuario
    if request.method == 'GET':
        return JsonResponse({
            'data': {
                'user_id': user.id,
                'email': user.email,
                'username': user.username,
                'nombre': user.first_name,
                'apellido': user.last_name,
                'cedula': profile.cedula if profile.cedula else '',
                'telefono': profile.telefono if profile.telefono else '',
                'is_active': user.is_active
            }
        }, status=200)

    # Aceptar POST, PUT o PATCH para edición
    if request.method not in ['POST', 'PUT', 'PATCH']:
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use POST, PUT o PATCH para editar usuarios'
        }, status=405)
    
    # Intentar parsear JSON si el content-type es application/json
    data = request.POST
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({
                'error': 'JSON inválido',
                'detalle': 'El body debe ser JSON válido'
            }, status=400)
    
    form = PersonalInfoForm(data, instance=profile)
    
    if form.is_valid():
        try:
            # Guardar información personal
            form.save()
            
            # Actualizar usuario de Django
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['email']
            user.first_name = form.cleaned_data['nombre']
            user.last_name = form.cleaned_data['apellido']
            user.save()
            
            return JsonResponse({
                'message': 'Usuario actualizado correctamente',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'nombre_completo': profile.nombre_completo
                }
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'error': 'Error al actualizar',
                'detalle': str(e)
            }, status=500)
    else:
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({
            'error': 'Datos de formulario inválidos',
            'errores': errors
        }, status=400)


#########################################

##########################################
# API - CONSUMIDA POR DISPOSITIVO IoT (ARDUINO)
##########################################

@csrf_exempt
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
    print(f"[ARDUINO] Headers: {dict(request.headers)}")
    print(f"[ARDUINO] Content-Type: {request.content_type}")
    print("="*80)
    
    if request.method != 'POST':
        print(f"[ARDUINO] ❌ Método {request.method} no permitido")
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use POST para enviar lecturas'
        }, status=405)
    
    try:
        # VALIDACIÓN OBLIGATORIA DE AUTENTICACIÓN
        api_key_valida = 'sk_arduino_controlbovino_2024'
        auth_header = request.headers.get('Authorization', '')
        
        print(f"[ARDUINO] Validando Authorization...")
        
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
        print(f"[ARDUINO] Body recibido (raw): {body_text[:500]}..." if len(body_text) > 500 else f"[ARDUINO] Body recibido (raw): {body_text}")
        
        if not body_text:
            print("[ARDUINO] ❌ Body vacío")
            return JsonResponse({
                'error': 'Body vacío',
                'detalle': 'El body no puede estar vacío'
            }, status=400)
        
        lecturaDecoded = json.loads(body_text)
        print(f"[ARDUINO] JSON parseado: {lecturaDecoded}")
        
        # Extraer datos del JSON
        collar_id = lecturaDecoded.get('collar_id')
        nombre_vaca = lecturaDecoded.get('nombre_vaca')
        mac_collar = lecturaDecoded.get('mac_collar')
        temperatura = lecturaDecoded.get('temperatura')
        # Si no se envía pulsaciones, generar aleatoriamente (simula sensor)
        pulsaciones = lecturaDecoded.get('pulsaciones', random.randint(41, 60))

        # Validar que todos los datos requeridos estén presentes
        print(f"[ARDUINO] Datos extraídos:")
        print(f"  - collar_id: {collar_id}")
        print(f"  - nombre_vaca: {nombre_vaca}")
        print(f"  - mac_collar: {mac_collar}")
        print(f"  - temperatura: {temperatura}")
        print(f"  - pulsaciones: {pulsaciones}")
        
        if not all([collar_id, nombre_vaca, mac_collar, temperatura]):
            print("[ARDUINO] ❌ Datos incompletos")
            return JsonResponse({
                'error': 'Datos incompletos',
                'detalle': 'Se requieren collar_id, nombre_vaca, mac_collar y temperatura',
                'recibido': lecturaDecoded
            }, status=400)
        
        # Convertir collar_id a entero (es un campo numérico en BD)
        try:
            collar_id = int(collar_id)
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'error': 'collar_id inválido',
                'detalle': f'collar_id debe ser un número entero: {str(e)}',
                'recibido': collar_id
            }, status=400)

        # Verificar o crear bovino
        print(f"[ARDUINO] Buscando/creando bovino con collar_id={collar_id}...")
        bovino, creado = Bovinos.objects.get_or_create(
            idCollar=collar_id,
            defaults={
                'macCollar': mac_collar,
                'nombre': nombre_vaca,
                'fecha_registro': datetime.now(),
                'activo': True
            }
        )
        print(f"[ARDUINO] Bovino {'CREADO' if creado else 'ENCONTRADO'}: {bovino.nombre} (ID: {bovino.id_Bovinos})")
        
        # Si el bovino ya existía, actualizar su nombre si cambió
        if not creado and bovino.nombre != nombre_vaca:
            print(f"[ARDUINO] Actualizando nombre: {bovino.nombre} -> {nombre_vaca}")
            bovino.nombre = nombre_vaca
            bovino.save(update_fields=['nombre'])

        # Crear registros de temperatura y pulsaciones
        print(f"[ARDUINO] Creando registros de sensores...")
        temperatura_obj = Temperatura.objects.create(valor=temperatura)
        pulsaciones_obj = Pulsaciones.objects.create(valor=pulsaciones)
        print(f"[ARDUINO] Temperatura ID: {temperatura_obj.id_Temperatura}, Pulsaciones ID: {pulsaciones_obj.id_Pulsaciones}")
        
        # Crear lectura
        lectura = Lectura.objects.create(
            id_Temperatura=temperatura_obj,
            id_Pulsaciones=pulsaciones_obj,
            id_Bovino=bovino,
            fecha_lectura=datetime.now(),
            hora_lectura=datetime.now().time()
        )
        print(f"[ARDUINO] Lectura creada ID: {lectura.id_Lectura}")
        print(f"[ARDUINO] Estado de salud: {lectura.estado_salud}")
        
        respuesta = {
            'mensaje': 'Datos guardados exitosamente',
            'data': {
                'lectura_id': lectura.id_Lectura,
                'bovino': bovino.nombre,
                'collar_id': bovino.idCollar,
                'temperatura': temperatura,
                'pulsaciones': pulsaciones,
                'estado_salud': lectura.estado_salud,
                'bovino_nuevo': creado,
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
        print(f"[ARDUINO] Creando registros de sensores...")
        temperatura_obj = Temperatura.objects.create(valor=temperatura)
        pulsaciones_obj = Pulsaciones.objects.create(valor=pulsaciones)
        print(f"[ARDUINO] Temperatura ID: {temperatura_obj.id_Temperatura}, Pulsaciones ID: {pulsaciones_obj.id_Pulsaciones}")
        
        # Crear lectura
        lectura = Lectura.objects.create(
            id_Temperatura=temperatura_obj,
            id_Pulsaciones=pulsaciones_obj,
            id_Bovino=bovino,
            fecha_lectura=datetime.now(),
            hora_lectura=datetime.now().time()
        )
        print(f"[ARDUINO] Lectura creada ID: {lectura.id_Lectura}")
        print(f"[ARDUINO] Estado de salud: {lectura.estado_salud}")
        
        respuesta = {
            'mensaje': 'Datos guardados exitosamente',
            'data': {
                'lectura_id': lectura.id_Lectura,
                'bovino': bovino.nombre,
                'collar_id': bovino.idCollar,
                'temperatura': temperatura,
                'pulsaciones': pulsaciones,
                'estado_salud': lectura.estado_salud,
                'bovino_nuevo': creado
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


# ============================================================================
# API: CONTROLES MANUALES - 3 lecturas por día (morning/afternoon/evening)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def controlManualRegistro(request):
    """
    POST: Registra un control manual de salud para un bovino
    GET: Obtiene los controles manuales del día actual para todos los bovinos
    
    Headers requeridos:
    - Authorization: Bearer {token}
    
    Body (POST):
    {
        "collar_id": 1,
        "fecha_control": "2026-01-15",
        "turno": "morning|afternoon|evening",
        "temperatura": 38.5,
        "pulsaciones": 72,
        "observaciones": "Texto opcional"
    }
    """
    print("\n" + "="*80)
    print("[CONTROL_MANUAL] Iniciando solicitud")
    print(f"[CONTROL_MANUAL] Método: {request.method}")
    print(f"[CONTROL_MANUAL] Usuario: {request.user}")
    print("="*80 + "\n")
    
    # Validar autenticación
    if not request.user.is_authenticated:
        print("[CONTROL_MANUAL] ❌ Usuario no autenticado")
        return JsonResponse({
            'error': 'No autorizado',
            'detalle': 'Autenticación requerida'
        }, status=401)
    
    if request.method == 'POST':
        try:
            from .serializers import ControlManualCreateSerializer
            
            body_text = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            print(f"[CONTROL_MANUAL] Body recibido: {body_text}")
            
            if not body_text:
                print("[CONTROL_MANUAL] ❌ Body vacío")
                return JsonResponse({
                    'error': 'Body vacío',
                    'detalle': 'El body no puede estar vacío'
                }, status=400)
            
            datos = json.loads(body_text)
            print(f"[CONTROL_MANUAL] Datos parseados: {datos}")
            
            # Crear control manual
            serializer = ControlManualCreateSerializer(
                data=datos,
                context={'request': request}
            )
            
            if serializer.is_valid():
                control = serializer.save()
                print(f"[CONTROL_MANUAL] ✅ Control registrado - ID: {control.id_ControlManual}")
                
                # Retornar datos del control creado
                from .serializers import ControlManualSerializer
                response_serializer = ControlManualSerializer(control)
                
                return JsonResponse({
                    'id': control.id_ControlManual,
                    'estado': 'creado',
                    'estado_salud': control.estado_salud,
                    'mensaje': f'Control de {control.id_Bovino.nombre} registrado exitosamente',
                    'data': response_serializer.data
                }, status=201)
            else:
                print(f"[CONTROL_MANUAL] ❌ Errores de validación: {serializer.errors}")
                return JsonResponse({
                    'error': 'Validación fallida',
                    'detalle': serializer.errors
                }, status=400)
        
        except Exception as e:
            print(f"[CONTROL_MANUAL] ❌ Error: {str(e)}")
            print(f"[CONTROL_MANUAL] Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'error': 'Error al procesar solicitud',
                'detalle': str(e)
            }, status=500)
    
    elif request.method == 'GET':
        try:
            from datetime import date
            from .serializers import ControlManualSerializer
            
            # Parámetros opcionales
            fecha_control = request.GET.get('fecha', str(date.today()))
            collar_id = request.GET.get('collar_id', None)
            turno = request.GET.get('turno', None)
            
            print(f"[CONTROL_MANUAL] Filtros: fecha={fecha_control}, collar_id={collar_id}, turno={turno}")
            
            # Construir queryset
            queryset = ControlManual.objects.filter(fecha_control=fecha_control)
            
            if collar_id:
                queryset = queryset.filter(id_Bovino__idCollar=collar_id)
            
            if turno:
                queryset = queryset.filter(turno=turno)
            
            serializer = ControlManualSerializer(queryset, many=True)
            
            print(f"[CONTROL_MANUAL] ✅ {len(serializer.data)} controles encontrados")
            
            return JsonResponse({
                'total': len(serializer.data),
                'fecha': fecha_control,
                'controles': serializer.data
            }, status=200)
        
        except Exception as e:
            print(f"[CONTROL_MANUAL] ❌ Error: {str(e)}")
            return JsonResponse({
                'error': 'Error al obtener controles',
                'detalle': str(e)
            }, status=500)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def controlManualDetalle(request, control_id):
    """
    PUT: Actualiza un control manual existente
    DELETE: Elimina un control manual
    
    Solo el usuario que creó el control puede modificarlo
    """
    print("\n" + "="*80)
    print(f"[CONTROL_MANUAL_DETALLE] Operación sobre control ID: {control_id}")
    print(f"[CONTROL_MANUAL_DETALLE] Método: {request.method}")
    print("="*80 + "\n")
    
    # Validar autenticación
    if not request.user.is_authenticated:
        print("[CONTROL_MANUAL_DETALLE] ❌ Usuario no autenticado")
        return JsonResponse({
            'error': 'No autorizado',
            'detalle': 'Autenticación requerida'
        }, status=401)
    
    try:
        control = ControlManual.objects.get(id_ControlManual=control_id)
    except ControlManual.DoesNotExist:
        print(f"[CONTROL_MANUAL_DETALLE] ❌ Control no encontrado: {control_id}")
        return JsonResponse({
            'error': 'No encontrado',
            'detalle': f'Control {control_id} no existe'
        }, status=404)
    
    # Verificar permisos (solo el usuario que creó puede modificar)
    if control.id_User != request.user:
        print(f"[CONTROL_MANUAL_DETALLE] ❌ Acceso denegado - Usuario: {request.user}, Creador: {control.id_User}")
        return JsonResponse({
            'error': 'Acceso denegado',
            'detalle': 'Solo el usuario que creó el control puede modificarlo'
        }, status=403)
    
    if request.method == 'PUT':
        try:
            from .serializers import ControlManualSerializer
            
            body_text = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            datos = json.loads(body_text)
            
            print(f"[CONTROL_MANUAL_DETALLE] Datos para actualización: {datos}")
            
            # Actualizar campos permitidos
            if 'temperatura' in datos:
                control.temperatura = datos['temperatura']
            if 'pulsaciones' in datos:
                control.pulsaciones = datos['pulsaciones']
            if 'observaciones' in datos:
                control.observaciones = datos['observaciones']
            if 'turno' in datos:
                control.turno = datos['turno']
            
            control.save()
            
            print(f"[CONTROL_MANUAL_DETALLE] ✅ Control actualizado")
            
            serializer = ControlManualSerializer(control)
            return JsonResponse({
                'id': control.id_ControlManual,
                'estado': 'actualizado',
                'estado_salud': control.estado_salud,
                'data': serializer.data
            }, status=200)
        
        except Exception as e:
            print(f"[CONTROL_MANUAL_DETALLE] ❌ Error: {str(e)}")
            return JsonResponse({
                'error': 'Error al actualizar control',
                'detalle': str(e)
            }, status=500)
    
    elif request.method == 'DELETE':
        try:
            bovino_nombre = control.id_Bovino.nombre
            control.delete()
            
            print(f"[CONTROL_MANUAL_DETALLE] ✅ Control eliminado para {bovino_nombre}")
            
            return JsonResponse({
                'estado': 'eliminado',
                'mensaje': f'Control de {bovino_nombre} eliminado exitosamente'
            }, status=200)
        
        except Exception as e:
            print(f"[CONTROL_MANUAL_DETALLE] ❌ Error al eliminar: {str(e)}")
            return JsonResponse({
                'error': 'Error al eliminar control',
                'detalle': str(e)
            }, status=500)


