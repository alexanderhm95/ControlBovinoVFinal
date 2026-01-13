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
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use POST para esta solicitud'
        }, status=405)
    
    # Obtener parámetros
    collar_id = request.POST.get('sensor')
    username = request.POST.get('username')
    
    # Validar parámetros requeridos
    if not collar_id or not username:
        return JsonResponse({
            'error': 'Parámetros incompletos',
            'detalle': 'Se requieren sensor y username'
        }, status=400)
    
    try:
        # Buscar bovino activo
        bovino = Bovinos.objects.filter(idCollar=collar_id, activo=True).first()
        if not bovino:
            return JsonResponse({
                'error': 'Bovino no encontrado',
                'detalle': f'No existe bovino activo con collar {collar_id}'
            }, status=404)
        
        # Buscar usuario
        user = User.objects.filter(username=username).first()
        if not user:
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

        # Verificar condiciones para registro de mañana
        if (checkingMorning(bovino) and 
            checkHoursMorning(dato.hora_lectura) and 
            checkDate(dato.fecha_lectura)):
            
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
            
            ControlMonitoreo.objects.create(
                id_Lectura=dato,
                id_User=user,
            )
            registro = True
            mensaje_registro = 'Registrado en turno de tarde'

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
        
        return JsonResponse({'reporte': reporte}, status=200)
        
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
    
    form = PersonalInfoForm(request.POST)
    
    if form.is_valid():
        try:
            # Verificar si ya existe un usuario con ese email
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                return JsonResponse({
                    'error': 'Email ya registrado',
                    'detalle': 'Ya existe un usuario con este email'
                }, status=400)
            
            # Crear usuario con el modelo CustomUserManager
            user = get_user_model().objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['cedula'],
                first_name=form.cleaned_data['nombre'],
                last_name=form.cleaned_data['apellido']
            )
            user.save()
            
            # Guardar información personal
            form.save()
            
            return JsonResponse({
                'message': 'Usuario creado exitosamente',
                'data': {
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
    else:
        # Retornar errores del formulario
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({
            'error': 'Datos de formulario inválidos',
            'errores': errors
        }, status=400)

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
    
    POST /api/user/<user_id>/edit/
    Body: form data con campos a actualizar
    
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

    if request.method != 'POST':
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use POST para editar usuarios'
        }, status=405)
    
    form = PersonalInfoForm(request.POST, instance=profile)
    
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
    
    POST /api/arduino/lectura/
    Body (JSON): {
        "collar_id": int,
        "nombre_vaca": str,
        "mac_collar": str,
        "temperatura": int,
        "pulsaciones": int (opcional, se genera aleatoriamente si no se proporciona)
    }
    
    Returns:
        JsonResponse con estado de guardado
    """
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Método no permitido',
            'detalle': 'Use POST para enviar lecturas'
        }, status=405)
    
    try:
        # Decodificar JSON del body
        body_unicode = request.body.decode('utf-8')
        lecturaDecoded = json.loads(body_unicode)
        
        # Extraer datos del JSON
        collar_id = lecturaDecoded.get('collar_id')
        nombre_vaca = lecturaDecoded.get('nombre_vaca')
        mac_collar = lecturaDecoded.get('mac_collar')
        temperatura = lecturaDecoded.get('temperatura')
        # Si no se envía pulsaciones, generar aleatoriamente (simula sensor)
        pulsaciones = lecturaDecoded.get('pulsaciones', random.randint(41, 60))

        # Validar que todos los datos requeridos estén presentes
        if not all([collar_id, nombre_vaca, mac_collar, temperatura]):
            return JsonResponse({
                'error': 'Datos incompletos',
                'detalle': 'Se requieren collar_id, nombre_vaca, mac_collar y temperatura',
                'recibido': lecturaDecoded
            }, status=400)

        # Verificar o crear bovino
        bovino, creado = Bovinos.objects.get_or_create(
            idCollar=collar_id,
            defaults={
                'macCollar': mac_collar,
                'nombre': nombre_vaca,
                'fecha_registro': datetime.now(),
                'activo': True
            }
        )
        
        # Si el bovino ya existía, actualizar su nombre si cambió
        if not creado and bovino.nombre != nombre_vaca:
            bovino.nombre = nombre_vaca
            bovino.save(update_fields=['nombre'])

        # Crear registros de temperatura y pulsaciones
        temperatura_obj = Temperatura.objects.create(valor=temperatura)
        pulsaciones_obj = Pulsaciones.objects.create(valor=pulsaciones)
        
        # Crear lectura
        lectura = Lectura.objects.create(
            id_Temperatura=temperatura_obj,
            id_Pulsaciones=pulsaciones_obj,
            id_Bovino=bovino,
            fecha_lectura=datetime.now(),
            hora_lectura=datetime.now().time()
        )
        
        return JsonResponse({
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
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'detalle': 'El body no es un JSON válido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }, status=500)


#########################################

