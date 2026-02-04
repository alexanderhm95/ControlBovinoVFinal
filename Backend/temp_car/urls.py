# En temperature_app/urls.py
from django.conf import settings
from . import views
from temp_car.views import *
from temp_car.user.users_views import *
from temp_car.logs_views import *
from django.urls import path
from django.conf.urls.static import static

urlpatterns = [
    ##################################
    #Rutas del Frontend
    ##################################
    #Ruta para el Inicio de Sesion
    path('', user_login,name='login'),
    path('logout/', user_logout, name='salir'),
    path('gestion/', listar_usuario, name='gestion'),    
    path('crear_usuario/', crear_usuario, name='crear_usuario'),  
    #path('editar_usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('editar_usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('changeState/<int:usuario_id>/', desactivar_usuario, name='changeState'),
    #Rutas para restablecer contraseña
    path('reset-password/', CustomPasswordResetView.as_view(), name='passwordReset'),
    path('reset-password/done/', ResetPasswordDoneView.as_view(), name='passwordResetDone'),
    path('reset-password/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='passwordResetConfirm'),
    path('reset-password/complete/',ResetPasswordCompleteView.as_view(), name='passwordResetComplete'),
    path('monitoreo_actual/', monitoreo_actual, name='monitoreo_actual'),
    path('reportes/', reportes, name='reportes'), 
    path('temperatura/', temperatura, name='temperatura'), 
    path('frecuencia/', frecuencia, name='frecuencia'),
    path('generar_pdf/', reporte_pdf, name='generar_pdf'),
    path('monitor/datos/<int:id_collar>/', views.dashBoardData, name='datos'),
    path('ultimo/registro/<int:collar_id>', views.ultimoRegistro, name='ultimo_registro'),    
    

    

    ######################################
    #Rutas de Plataforma Movil  
    ######################################
    path('api/movil/login/', LoginView1.as_view(), name='api-login'),                     # Api para el login
    path('api/movil/datos/', views.registrar_datos_sensores, name='registrar_sensores'),  # Api POST para registrar datos de sensores
    path('api/movil/datos/<int:collar_id>/', views.obtener_datos_collar, name='datos_collar_get'),  # Api GET para obtener datos por collar ID
    path('api/movil/verificar-lectura/<int:collar_id>/', views.verificar_lectura_turno, name='verificar_lectura'),  # Api GET para verificar lectura del turno
    path('api/editar/<int:user_id>/', views.apiEdit, name='editar'),  # Api para editar usuario
    #############################################################
    

    ######################################
    #Ruta para el Arduino 
    ######################################
    path('api/arduino/monitoreo/', views.lecturaDatosArduino, name='recibir_datos2'),
    path('api/arduino/monitoreo', views.lecturaDatosArduino, name='recibir_datos'),  # Sin slash final para POST sin redirección
    
    ######################################
    # CONTROLES DE MONITOREO
    ######################################
    path('api/controles-monitoreo/', views.controlMonitoreoRegistro, name='control_monitoreo_registro'),
    path('api/controles-monitoreo/<int:control_id>/', views.controlMonitoreoDetalle, name='control_monitoreo_detalle'),
    ######################################

    ######################################
    # RUTAS PARA VISUALIZACIÓN DE LOGS
    ######################################
    path('logs/', view_logs_dashboard, name='view_logs'),
    path('logs/file/<str:filename>/', get_log_content, name='get_log_content'),
    path('logs/download/<str:filename>/', get_log_file, name='download_log'),
    path('logs/clear/<str:filename>/', clear_log_file, name='clear_log'),
    path('logs/stats/', logs_api_stats, name='logs_stats'),
    ######################################

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#handler404 = 'temp_car.views.error_404_view'
