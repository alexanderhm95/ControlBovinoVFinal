"""
Serializers para la API REST del Control Bovino
Convierte modelos Django a JSON y valida datos de entrada
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Bovinos, Temperatura, Pulsaciones, Lectura, 
    ControlMonitoreo, ControlManual, PersonalInfo
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
    """Serializer para controles de monitoreo"""
    lectura = LecturaSerializer(source='id_Lectura', read_only=True)
    usuario = serializers.StringRelatedField(source='id_User', read_only=True)
    
    class Meta:
        model = ControlMonitoreo
        fields = [
            'id_Control', 'lectura', 'usuario', 'fecha_lectura', 
            'hora_lectura', 'observaciones', 'accion_tomada'
        ]


class ControlManualSerializer(serializers.ModelSerializer):
    """Serializer para controles manuales de salud"""
    bovino = BovinosSerializer(source='id_Bovino', read_only=True)
    usuario = serializers.StringRelatedField(source='id_User', read_only=True)
    turno_display = serializers.CharField(source='get_turno_display', read_only=True)
    
    class Meta:
        model = ControlManual
        fields = [
            'id_ControlManual', 'bovino', 'usuario', 'fecha_control', 
            'turno', 'turno_display', 'temperatura', 'pulsaciones', 
            'observaciones', 'estado_salud', 'fecha_registro', 'fecha_actualizacion'
        ]
        read_only_fields = ['id_ControlManual', 'bovino', 'usuario', 'estado_salud', 
                           'fecha_registro', 'fecha_actualizacion']


class ControlManualCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear controles manuales"""
    collar_id = serializers.IntegerField(write_only=True, help_text="ID del collar del bovino")
    
    class Meta:
        model = ControlManual
        fields = [
            'collar_id', 'fecha_control', 'turno', 'temperatura', 
            'pulsaciones', 'observaciones'
        ]
    
    def validate_turno(self, value):
        """Valida que el turno sea uno de los válidos"""
        valid_turnos = ['morning', 'afternoon', 'evening']
        if value not in valid_turnos:
            raise serializers.ValidationError(
                f"El turno debe ser uno de: {', '.join(valid_turnos)}"
            )
        return value
    
    def create(self, validated_data):
        """Crea un nuevo control manual"""
        collar_id = validated_data.pop('collar_id')
        user = self.context['request'].user
        
        try:
            bovino = Bovinos.objects.get(idCollar=collar_id)
        except Bovinos.DoesNotExist:
            raise serializers.ValidationError(f"No existe bovino con ID de collar: {collar_id}")
        
        # Verificar si ya existe un control para ese bovino, fecha y turno
        existing = ControlManual.objects.filter(
            id_Bovino=bovino,
            fecha_control=validated_data['fecha_control'],
            turno=validated_data['turno']
        ).first()
        
        if existing:
            raise serializers.ValidationError(
                f"Ya existe un control para {bovino.nombre} en esta fecha y turno"
            )
        
        control = ControlManual.objects.create(
            id_Bovino=bovino,
            id_User=user,
            **validated_data
        )
        return control
