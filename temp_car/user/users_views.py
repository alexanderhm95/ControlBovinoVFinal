"""
Vistas de gestión de usuarios del sistema Control Bovino
Incluye autenticación, CRUD de usuarios y recuperación de contraseña
"""

# Django core imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View

# Local imports
from temp_car.forms import PersonalInfoForm, EditPersonalInfoForm, EditUserForm
from temp_car.models import PersonalInfo

####################################
# AUTENTICACIÓN
####################################

def user_login(request):
    """
    Vista de inicio de sesión de usuarios
    Redirige al dashboard si la autenticación es exitosa
    
    POST: Procesa credenciales
    GET: Muestra formulario de login
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validar que se proporcionaron ambos campos
        if not username or not password:
            messages.error(request, 'Por favor ingrese usuario y contraseña.')
            return render(request, 'appMonitor/login.html')
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Bienvenido {user.first_name}!')
                return redirect('monitoreo_actual')
            else:
                messages.error(request, 'Esta cuenta está desactivada. Contacte al administrador.')
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo nuevamente.')
    
    return render(request, 'appMonitor/login.html')


def user_logout(request):
    """
    Vista de cierre de sesión
    Limpia la sesión y redirige al inicio
    """
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('/')


####################################
# REGISTRO DE USUARIOS
####################################

def crear_usuario(request):
    """
    Vista de registro de nuevos usuarios
    Crea usuario de Django y perfil PersonalInfo asociado
    
    POST: Procesa formulario de registro
    GET: Muestra formulario vacío
    """
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST)
        
        if form.is_valid():
            try:
                # Verificar si ya existe un usuario con ese email
                if User.objects.filter(email=form.cleaned_data['email']).exists():
                    messages.error(request, 'Ya existe un usuario con este correo electrónico.')
                    return render(request, 'appMonitor/user/register.html', {'form': form})
                
                # Crear usuario con el modelo CustomUserManager
                user = get_user_model().objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['cedula'],  # Usar cédula como contraseña inicial
                    first_name=form.cleaned_data['nombre'],
                    last_name=form.cleaned_data['apellido']
                )
                user.save()
                
                # Guardar información personal
                form.save()

                # Enviar correo de bienvenida con enlace para establecer contraseña
                try:
                    subject = 'Bienvenido a Control Bovino'
                    email_template_name = 'appMonitor/user/new_user_email.txt'
                    context = {
                        'email': user.email,
                        'domain': request.META.get('HTTP_HOST', 'localhost'),
                        'site_name': 'Control y Monitoreo de Constantes Fisiológicas UNL',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }

                    email_content = render_to_string(email_template_name, context)

                    send_mail(
                        subject=subject,
                        message=email_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False
                    )
                except Exception as e:
                    # No detener el flujo por un fallo en el correo; notificar al admin/usuario
                    messages.warning(request, f'Usuario creado pero no se pudo enviar correo: {str(e)}')

                messages.success(request, 'Usuario creado exitosamente. Puede iniciar sesión.')
                return redirect('/')
                
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
                return render(request, 'appMonitor/user/register.html', {'form': form})
        else:
            # Si hay errores de validación, mostrarlos
            messages.error(request, 'Por favor corrija los errores en el formulario.')
            return render(request, 'appMonitor/user/register.html', {'form': form})
    else:
        # Método GET: mostrar formulario vacío
        form = PersonalInfoForm()
        return render(request, 'appMonitor/user/register.html', {'form': form})
####################################
# GESTIÓN DE USUARIOS
####################################

@login_required
def listar_usuario(request):
    """
    Vista de listado de usuarios para administradores
    Excluye superusuarios y muestra información de perfil
    
    Returns:
        Template con diccionario de usuarios
    """
    try:
        # Obtener todos los usuarios excepto superusuarios
        usuario_queryset = User.objects.filter(is_superuser=False).order_by('-date_joined')
        
        # Optimizar obteniendo todos los perfiles de una vez
        profiles_dict = {
            profile.email: profile 
            for profile in PersonalInfo.objects.all()
        }
        
        usuarios = {}
        
        for user in usuario_queryset:
            profile = profiles_dict.get(user.email)
            
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
                'fecha_registro': user.date_joined.strftime('%Y-%m-%d') if user.date_joined else "N/A",
            }
        
        context = {
            'usuarios': usuarios,
            'total_usuarios': len(usuarios)
        }
        
        return render(request, 'appMonitor/user/listar.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar usuarios: {str(e)}')
        return render(request, 'appMonitor/user/listar.html', {'usuarios': {}, 'total_usuarios': 0})


@login_required
def desactivar_usuario(request, usuario_id):
    """
    Vista para activar/desactivar usuarios
    Toggle del estado is_active del usuario
    
    Args:
        usuario_id: ID del usuario a activar/desactivar
    
    Returns:
        Redirect a lista de gestión de usuarios
    """
    try:
        usuario = get_object_or_404(User, id=usuario_id)
        
        # Prevenir desactivación de superusuarios
        if usuario.is_superuser:
            messages.warning(request, 'No se puede desactivar a un superusuario.')
            return redirect('gestion')
        
        # Prevenir que un usuario se desactive a sí mismo
        if usuario.id == request.user.id:
            messages.warning(request, 'No puedes desactivar tu propia cuenta.')
            return redirect('gestion')
        
        # Toggle del estado activo
        if usuario.is_active:
            usuario.is_active = False
            messages.warning(request, f'Usuario {usuario.username} desactivado correctamente.')
        else:
            usuario.is_active = True
            messages.success(request, f'Usuario {usuario.username} activado correctamente.')
        
        usuario.save()
        
    except Exception as e:
        messages.error(request, f'Error al cambiar estado del usuario: {str(e)}')
    
    return redirect('gestion')

@login_required
def editar_usuario(request, user_id):
    """
    Vista para editar información de usuarios
    Permite actualizar datos personales y permisos
    
    Args:
        user_id: ID del usuario a editar
        
    POST: Procesa actualización
    GET: Muestra formularios de edición
    """
    try:
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(PersonalInfo, email=user.email)
        
        # Prevenir edición de superusuarios por no-superusuarios
        if user.is_superuser and not request.user.is_superuser:
            messages.error(request, 'No tiene permisos para editar a un superusuario.')
            return redirect('gestion')

        if request.method == 'POST':
            personal_info_form = EditPersonalInfoForm(request.POST, instance=profile)
            user_form = EditUserForm(request.POST, instance=user)

            if personal_info_form.is_valid() and user_form.is_valid():
                try:
                    # Verificar si el nuevo email ya existe (excepto el actual)
                    nuevo_email = personal_info_form.cleaned_data['email']
                    if User.objects.filter(email=nuevo_email).exclude(id=user.id).exists():
                        messages.error(request, 'Ya existe otro usuario con este correo electrónico.')
                        return render(request, 'appMonitor/user/editar.html', {
                            'personal_info_form': personal_info_form,
                            'user_form': user_form,
                            'profile': profile
                        })
                    
                    # Guardar información personal
                    personal_info_form.save()

                    # Actualizar usuario
                    user.email = nuevo_email
                    user.username = nuevo_email
                    user.first_name = personal_info_form.cleaned_data['nombre']
                    user.last_name = personal_info_form.cleaned_data['apellido']
                    user.is_staff = user_form.cleaned_data['is_staff']
                    user.save()

                    messages.success(request, f'Usuario {user.username} actualizado correctamente.')
                    return redirect('gestion')
                    
                except Exception as e:
                    messages.error(request, f'Error al guardar cambios: {str(e)}')
            else:
                messages.error(request, 'Por favor corrija los errores en el formulario.')
        else:
            # Método GET: cargar formularios con datos actuales
            personal_info_form = EditPersonalInfoForm(instance=profile)
            user_form = EditUserForm(instance=user)

        context = {
            'personal_info_form': personal_info_form,
            'user_form': user_form,
            'profile': profile,
            'usuario_editado': user
        }
        
        return render(request, 'appMonitor/user/editar.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al editar usuario: {str(e)}')
        return redirect('gestion')




####################################
# RECUPERACIÓN DE CONTRASEÑA
####################################

class CustomPasswordResetView(View):
    """
    Vista para solicitar restablecimiento de contraseña
    Envía email con enlace de recuperación
    
    GET: Muestra formulario
    POST: Procesa solicitud y envía email
    """
    template_name = 'appMonitor/resetPassword/password_reset_form.html'

    def get(self, request):
        form = PasswordResetForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email, is_active=True)
            
            if associated_users.exists():
                try:
                    for user in associated_users:
                        subject = 'Restablecimiento de contraseña - Control Bovino'
                        email_template_name = 'appMonitor/resetPassword/password_reset_email.html'
                        
                        context = {
                            'email': user.email,
                            'domain': request.META.get('HTTP_HOST', 'localhost'),
                            'site_name': 'Control y Monitoreo de Constantes Fisiológicas UNL',
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'user': user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'https' if request.is_secure() else 'http',
                        }
                        
                        email_content = render_to_string(email_template_name, context)
                        
                        # Enviar correo
                        send_mail(
                            subject=subject,
                            message=email_content,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=False
                        )
                    
                    messages.success(request, 'Se ha enviado un correo con instrucciones para restablecer su contraseña.')
                    return redirect('passwordResetDone')
                    
                except Exception as e:
                    messages.error(request, f'Error al enviar el correo: {str(e)}')
            else:
                # Por seguridad, no revelamos si el email existe o no
                messages.info(request, 'Si el correo existe en nuestro sistema, recibirá instrucciones para restablecer su contraseña.')
                return redirect('passwordResetDone')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
        
        return render(request, self.template_name, {'form': form})

class ResetPasswordDoneView(View):
    """
    Vista de confirmación de envío de email de recuperación
    Muestra mensaje informando que se envió el correo
    """
    template_name = 'appMonitor/resetPassword/password_reset_done.html'

    def get(self, request):
        return render(request, self.template_name)


class CustomPasswordResetConfirmView(View):
    """
    Vista para confirmar restablecimiento de contraseña
    Valida el token y permite establecer nueva contraseña
    
    GET: Valida enlace y muestra formulario
    POST: Procesa nueva contraseña
    """
    template_name = 'appMonitor/resetPassword/password_reset_confirm.html'

    def get(self, request, uidb64=None, token=None):
        try:
            # Decodificar el UID del usuario
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            
            # Verificar que el token sea válido
            if default_token_generator.check_token(user, token):
                form = SetPasswordForm(user)
                return render(request, self.template_name, {
                    'form': form,
                    'validlink': True,
                    'uidb64': uidb64,
                    'token': token
                })
            else:
                messages.error(
                    request,
                    'El enlace de restablecimiento de contraseña no es válido o ya fue usado. '
                    'Por favor solicite un nuevo restablecimiento.'
                )
                return render(request, self.template_name, {'validlink': False})
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(
                request,
                'El enlace de restablecimiento de contraseña no es válido. '
                'Por favor solicite un nuevo restablecimiento.'
            )
            return render(request, self.template_name, {'validlink': False})

    def post(self, request, uidb64=None, token=None):
        try:
            # Decodificar el UID del usuario
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            
            # Procesar formulario de nueva contraseña
            form = SetPasswordForm(user, request.POST)
            
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    'Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión.'
                )
                return redirect('passwordResetComplete')
            else:
                # Mostrar errores de validación
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
            
            return render(request, self.template_name, {
                'form': form,
                'validlink': True,
                'uidb64': uidb64,
                'token': token
            })
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(
                request,
                'El enlace de restablecimiento de contraseña no es válido. '
                'Por favor solicite un nuevo restablecimiento.'
            )
            return render(request, self.template_name, {'validlink': False})


class ResetPasswordCompleteView(View):
    """
    Vista de confirmación final de restablecimiento de contraseña
    Muestra mensaje de éxito y enlace para iniciar sesión
    """
    template_name = 'appMonitor/resetPassword/password_reset_complete.html'

    def get(self, request):
        return render(request, self.template_name)
