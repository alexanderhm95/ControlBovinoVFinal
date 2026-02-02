"""
Serializers para la API REST del Control Bovino
Convierte modelos Django a JSON y valida datos de entrada
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Bovinos, Temperatura, Pulsaciones, Lectura, 
    ControlMonitoreo, PersonalInfo
)


class BovinosSerializer(serializers.ModelSerializer):
    """Serializer para información de bovinos"""
    class Meta:
        model = Bovinos
        fields = ['id_Bovinos', 'idCollar', 'macCollar', 'nombre', 'fecha_registro', 'activo']


class TemperaturaSerializer(serializers.ModelSerializer):
    """Serializer para datos de temperatura"""
    class Meta:
        model = Temperatura
        fields = ['id_Temperatura', 'valor']


class PulsacionesSerializer(serializers.ModelSerializer):
    """Serializer para datos de pulsaciones"""
    class Meta:
        model = Pulsaciones
        fields = ['id_Pulsaciones', 'valor']


class LecturaSerializer(serializers.ModelSerializer):
    """Serializer para lecturas de sensores"""
    temperatura = serializers.SerializerMethodField()
    pulsaciones = serializers.SerializerMethodField()
    bovino = BovinosSerializer(source='id_Bovino', read_only=True)
    
    class Meta:
        model = Lectura
        fields = [
            'id_Lectura', 'temperatura', 'pulsaciones', 'fecha_lectura', 
            'hora_lectura', 'bovino', 'temperatura_normal', 'pulsaciones_normales',
            'estado_salud'
        ]
    
    def get_temperatura(self, obj):
        return obj.temperatura_valor
    
    def get_pulsaciones(self, obj):
        return obj.pulsaciones_valor


class ControlMonitoreoSerializer(serializers.ModelSerializer):
    """Serializer para controles de monitoreo - integra controles automáticos y manuales"""
    lectura = LecturaSerializer(source='id_Lectura', read_only=True)
    usuario = serializers.StringRelatedField(source='id_User', read_only=True)
    
    class Meta:
        model = ControlMonitoreo
        fields = [
            'id_Control', 'lectura', 'usuario', 'fecha_lectura', 
            'hora_lectura', 'turno', 'temperatura', 'pulsaciones',
            'estado_salud', 'observaciones', 'accion_tomada',
            'fecha_registro', 'fecha_actualizacion'
        ]
        read_only_fields = ['id_Control', 'estado_salud', 'fecha_registro', 'fecha_actualizacion']
