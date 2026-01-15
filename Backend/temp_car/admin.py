"""
Configuración del panel de administración de Django
para los modelos de Control Bovino
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Temperatura,
    Pulsaciones,
    Bovinos,
    Lectura,
    PersonalInfo,
    ControlMonitoreo
)


@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    """Administración de información personal"""
    list_display = ['cedula', 'nombre_completo', 'telefono', 'email']
    search_fields = ['cedula', 'nombre', 'apellido', 'email']
    list_filter = []
    ordering = ['apellido', 'nombre']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'cedula')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email')
        }),
    )


@admin.register(Temperatura)
class TemperaturaAdmin(admin.ModelAdmin):
    """Administración de temperaturas (Legacy)"""
    list_display = ['id_Temperatura', 'valor']
    search_fields = ['valor']
    ordering = ['-id_Temperatura']


@admin.register(Pulsaciones)
class PulsacionesAdmin(admin.ModelAdmin):
    """Administración de pulsaciones (Legacy)"""
    list_display = ['id_Pulsaciones', 'valor']
    search_fields = ['valor']
    ordering = ['-id_Pulsaciones']


@admin.register(Bovinos)
class BovinosAdmin(admin.ModelAdmin):
    """Administración de bovinos"""
    list_display = ['nombre', 'idCollar', 'macCollar', 'fecha_registro', 'activo_badge']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre', 'idCollar', 'macCollar']
    ordering = ['-fecha_registro', 'nombre']
    date_hierarchy = 'fecha_registro'
    
    fieldsets = (
        ('Información del Bovino', {
            'fields': ('nombre', 'activo')
        }),
        ('Dispositivo', {
            'fields': ('idCollar', 'macCollar'),
            'description': 'Información del collar sensor'
        }),
        ('Registro', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = []
    
    def activo_badge(self, obj):
        """Muestra un badge visual para el estado activo"""
        if obj.activo:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Activo</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Inactivo</span>'
        )
    activo_badge.short_description = 'Estado'


@admin.register(Lectura)
class LecturaAdmin(admin.ModelAdmin):
    """Administración de lecturas"""
    list_display = [
        'id_Lectura',
        'id_Bovino',
        'temperatura_display',
        'pulsaciones_display',
        'fecha_lectura',
        'hora_lectura',
        'estado_badge'
    ]
    list_filter = ['fecha_lectura', 'id_Bovino']
    search_fields = ['id_Bovino__nombre', 'id_Lectura']
    ordering = ['-fecha_lectura', '-hora_lectura']
    date_hierarchy = 'fecha_lectura'
    
    fieldsets = (
        ('Bovino', {
            'fields': ('id_Bovino',)
        }),
        ('Mediciones', {
            'fields': ('id_Temperatura', 'id_Pulsaciones')
        }),
        ('Fecha y Hora', {
            'fields': ('fecha_lectura', 'hora_lectura'),
            'classes': ('collapse',)
        }),
    )
    
    def temperatura_display(self, obj):
        """Muestra la temperatura con formato y color"""
        valor = obj.temperatura_valor
        if valor is None:
            return '-'
        
        if obj.temperatura_normal:
            color = '#28a745'  # Verde
        else:
            color = '#dc3545'  # Rojo
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} °C</span>',
            color, valor
        )
    temperatura_display.short_description = 'Temperatura'
    
    def pulsaciones_display(self, obj):
        """Muestra las pulsaciones con formato y color"""
        valor = obj.pulsaciones_valor
        if valor is None:
            return '-'
        
        if obj.pulsaciones_normales:
            color = '#28a745'  # Verde
        else:
            color = '#dc3545'  # Rojo
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} BPM</span>',
            color, valor
        )
    pulsaciones_display.short_description = 'Pulsaciones'
    
    def estado_badge(self, obj):
        """Muestra el estado de salud con badge"""
        estado = obj.estado_salud
        
        if estado == 'Normal':
            color = '#28a745'
            icon = '✓'
        elif estado == 'Alerta':
            color = '#ffc107'
            icon = '⚠'
        elif estado == 'Crítico':
            color = '#dc3545'
            icon = '✗'
        else:
            color = '#6c757d'
            icon = '?'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{} {}</span>',
            color, icon, estado
        )
    estado_badge.short_description = 'Estado'


@admin.register(ControlMonitoreo)
class ControlMonitoreoAdmin(admin.ModelAdmin):
    """Administración de controles de monitoreo"""
    list_display = [
        'id_Control',
        'bovino_nombre',
        'id_User',
        'fecha_lectura',
        'hora_lectura',
        'tiene_observaciones',
        'tiene_accion'
    ]
    list_filter = ['fecha_lectura', 'id_User']
    search_fields = [
        'id_Lectura__id_Bovino__nombre',
        'id_User__username',
        'observaciones',
        'accion_tomada'
    ]
    ordering = ['-fecha_lectura', '-hora_lectura']
    date_hierarchy = 'fecha_lectura'
    
    fieldsets = (
        ('Lectura', {
            'fields': ('id_Lectura',)
        }),
        ('Control', {
            'fields': ('id_User', 'fecha_lectura', 'hora_lectura')
        }),
        ('Detalles', {
            'fields': ('observaciones', 'accion_tomada'),
            'description': 'Observaciones y acciones tomadas por el veterinario'
        }),
    )
    
    def bovino_nombre(self, obj):
        """Muestra el nombre del bovino de la lectura"""
        return obj.id_Lectura.id_Bovino.nombre
    bovino_nombre.short_description = 'Bovino'
    bovino_nombre.admin_order_field = 'id_Lectura__id_Bovino__nombre'
    
    def tiene_observaciones(self, obj):
        """Indica si tiene observaciones"""
        if obj.observaciones:
            return format_html(
                '<span style="color: #28a745;">✓</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗</span>'
        )
    tiene_observaciones.short_description = 'Obs.'
    tiene_observaciones.boolean = True
    
    def tiene_accion(self, obj):
        """Indica si tiene acción tomada"""
        if obj.accion_tomada:
            return format_html(
                '<span style="color: #28a745;">✓</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗</span>'
        )
    tiene_accion.short_description = 'Acción'
    tiene_accion.boolean = True


# Personalización del sitio de administración
admin.site.site_header = 'Control Bovino - Administración'
admin.site.site_title = 'Control Bovino Admin'
admin.site.index_title = 'Panel de Control'