"""
Modelos de la aplicación de Control Bovino
Gestiona información de bovinos, lecturas de sensores y controles de monitoreo
"""

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Bovinos(models.Model):
    """Información de bovinos registrados en el sistema"""
    id_Bovinos = models.AutoField(primary_key=True)
    idCollar = models.IntegerField(
        'ID del Collar',
        unique=True,
        db_index=True
    )
    macCollar = models.CharField(
        'MAC del Collar',
        max_length=100,
        blank=True,
        null=True,
        help_text='Dirección MAC del collar sensor'
    )
    nombre = models.CharField(
        'Nombre',
        max_length=100
    )
    fecha_registro = models.DateField(
        'Fecha de Registro',
        default=timezone.now
    )
    activo = models.BooleanField(
        'Activo',
        default=True,
        help_text='Indica si el bovino está activo en el sistema'
    )
    
    class Meta:
        verbose_name = 'Bovino'
        verbose_name_plural = 'Bovinos'
        ordering = ['-fecha_registro', 'nombre']
        indexes = [
            models.Index(fields=['idCollar']),
            models.Index(fields=['macCollar']),
            models.Index(fields=['-fecha_registro']),
        ]

    def __str__(self):
        return f"{self.nombre} (Collar: {self.idCollar})"

class PersonalInfo(models.Model):
    """Información personal de contacto"""
    cedula = models.CharField(
        'Cédula',
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )
    telefono = models.CharField(
        'Teléfono',
        max_length=15,
        blank=True,
        null=True
    )
    nombre = models.CharField(
        'Nombre',
        max_length=50,
        blank=True,
        null=True
    )
    apellido = models.CharField(
        'Apellido',
        max_length=50,
        blank=True,
        null=True
    )
    email = models.EmailField(
        'Email',
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Información Personal'
        verbose_name_plural = 'Información Personal'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['cedula']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.email or self.cedula or "Sin identificación"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo"""
        return f"{self.nombre} {self.apellido}".strip()


class Temperatura(models.Model):
    """Modelo legacy de temperatura - se mantiene para compatibilidad"""
    id_Temperatura = models.AutoField(primary_key=True)
    valor = models.FloatField()

    def __str__(self):
        return str(self.valor)

    class Meta:
        verbose_name = 'Temperatura'
        verbose_name_plural = 'Temperaturas'


class Pulsaciones(models.Model):
    """Modelo legacy de pulsaciones - se mantiene para compatibilidad"""
    id_Pulsaciones = models.AutoField(primary_key=True)
    valor = models.IntegerField()

    def __str__(self):
        return str(self.valor)

    class Meta:
        verbose_name = 'Pulsación'
        verbose_name_plural = 'Pulsaciones'


class Lectura(models.Model):
    """Lectura de sensores de bovino"""
    id_Lectura = models.AutoField(primary_key=True)
    id_Temperatura = models.ForeignKey(
        Temperatura,
        on_delete=models.CASCADE,
        verbose_name='Temperatura'
    )
    id_Pulsaciones = models.ForeignKey(
        Pulsaciones,
        on_delete=models.CASCADE,
        verbose_name='Pulsaciones'
    )
    fecha_lectura = models.DateField(
        'Fecha de Lectura',
        default=timezone.now,
        db_index=True
    )
    hora_lectura = models.TimeField(
        'Hora de Lectura',
        default=timezone.now,
        db_index=True
    )
    id_Bovino = models.ForeignKey(
        Bovinos,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Bovino'
    )
    fuente = models.CharField(
        'Fuente de Datos',
        max_length=20,
        choices=[
            ('arduino', 'Arduino/Collar'),
            ('app_movil', 'App Móvil'),
            ('manual', 'Manual')
        ],
        default='arduino',
        null=True,
        blank=True,
        db_index=True,
        help_text='Origen de la lectura: Arduino (collar), App Móvil o Manual'
    )

    class Meta:
        verbose_name = 'Lectura'
        verbose_name_plural = 'Lecturas'
        ordering = ['-fecha_lectura', '-hora_lectura']
        indexes = [
            models.Index(fields=['id_Bovino', '-fecha_lectura', '-hora_lectura']),
            models.Index(fields=['-fecha_lectura', '-hora_lectura']),
        ]
        get_latest_by = 'fecha_lectura'

    def __str__(self):
        return f"{self.id_Lectura} - {self.id_Bovino.nombre} - {self.fecha_lectura} - {self.hora_lectura}"

    def hora_lectura_guayaquil(self):
        """Retorna la hora de lectura (ya está en zona horaria de Guayaquil)"""
        return str(self.hora_lectura)
    
    hora_lectura_guayaquil.short_description = 'Hora (Guayaquil)'
    
    @property
    def temperatura_valor(self):
        """Retorna el valor de temperatura"""
        return self.id_Temperatura.valor if self.id_Temperatura else None

    @property
    def pulsaciones_valor(self):
        """Retorna el valor de pulsaciones"""
        return self.id_Pulsaciones.valor if self.id_Pulsaciones else None

    @property
    def temperatura_normal(self):
        """Verifica si la temperatura está en rango normal (38-39°C)"""
        if self.id_Temperatura:
            return 38 <= self.id_Temperatura.valor <= 39
        return None

    @property
    def pulsaciones_normales(self):
        """Verifica si las pulsaciones están en rango normal (60-80 BPM)"""
        if self.id_Pulsaciones:
            return 60 <= self.id_Pulsaciones.valor <= 80
        return None

    @property
    def estado_salud(self):
        """Retorna el estado general de salud basado en temperatura (rangos para vacas lecheras)"""
        temp = self.temperatura_valor
        
        if temp is None:
            return 'Desconocido'
        
        # Rangos específicos para vacas lecheras (bovinos adultos)
        # Normal: 38-39°C
        # Alerta/Fiebre leve: 39-40°C
        # Crítico: >40°C o <36°C (hipotermia)
        if temp < 36:
            return 'Crítico'  # Hipotermia
        elif 36 <= temp < 38:
            return 'Alerta'  # Temperatura baja (subclinicamente baja)
        elif 38 <= temp <= 39:
            return 'Normal'  # Rango normal para bovinos
        elif 39 < temp <= 40:
            return 'Alerta'  # Fiebre leve
        else:  # temp > 40
            return 'Crítico'  # Fiebre alta


class ControlMonitoreo(models.Model):
    """
    Control y seguimiento de salud - Integra controles automáticos (de sensores) 
    y controles manuales (registrados por usuario) en una única entidad
    """
    # Opciones de turno
    TURNO_CHOICES = [
        ('morning', 'Mañana (06:00 - 12:00)'),
        ('afternoon', 'Tarde (12:00 - 18:00)'),
        ('evening', 'Noche (18:00 - 23:59)'),
        ('night', 'Madrugada (00:00 - 06:00)'),
    ]
    
    # Opciones de estado de salud
    ESTADO_SALUD_CHOICES = [
        ('Normal', 'Normal (38.0-39.0°C)'),
        ('Alerta', 'Alerta (39.0-40.0°C)'),
        ('Crítico', 'Crítico (>40.0°C)'),
    ]
    
    id_Control = models.AutoField(primary_key=True)
    id_Lectura = models.ForeignKey(
        Lectura,
        on_delete=models.CASCADE,
        related_name='controles',
        verbose_name='Lectura',
        null=True,
        blank=True,
        help_text='Lectura automática del sensor (puede ser nula para controles puramente manuales)'
    )
    id_User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='controles_monitoreo',
        verbose_name='Usuario que registra'
    )
    fecha_lectura = models.DateField(
        'Fecha del Control',
        default=timezone.now,
        db_index=True
    )
    hora_lectura = models.TimeField(
        'Hora del Control',
        default=timezone.now
    )
    turno = models.CharField(
        'Turno',
        max_length=10,
        choices=TURNO_CHOICES,
        default='morning',
        help_text='Turno del día en que se realiza el control'
    )
    # Datos de medición (puede venir del sensor o ser registrado manualmente)
    temperatura = models.FloatField(
        'Temperatura (°C)',
        validators=[MinValueValidator(35.0), MaxValueValidator(42.0)],
        null=True,
        blank=True,
        help_text='Temperatura corporal del bovino'
    )
    pulsaciones = models.IntegerField(
        'Pulsaciones (BPM)',
        validators=[MinValueValidator(40), MaxValueValidator(150)],
        null=True,
        blank=True,
        help_text='Pulsaciones por minuto del bovino'
    )
    estado_salud = models.CharField(
        'Estado de Salud',
        max_length=20,
        choices=ESTADO_SALUD_CHOICES,
        default='Normal',
        db_index=True,
        help_text='Estado de salud calculado automáticamente'
    )
    observaciones = models.TextField(
        'Observaciones',
        blank=True,
        null=True,
        help_text='Observaciones del veterinario o encargado'
    )
    accion_tomada = models.CharField(
        'Acción Tomada',
        max_length=200,
        blank=True,
        null=True,
        help_text='Acción o tratamiento aplicado'
    )
    fecha_registro = models.DateTimeField(
        'Fecha de Registro',
        auto_now_add=True,
        null=True,
        blank=True
    )
    fecha_actualizacion = models.DateTimeField(
        'Fecha de Actualización',
        auto_now=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Control de Monitoreo'
        verbose_name_plural = 'Controles de Monitoreo'
        ordering = ['-fecha_lectura', '-hora_lectura']
        unique_together = [['id_Lectura', 'turno']]  # Un control por lectura y turno
        indexes = [
            models.Index(fields=['id_User', '-fecha_lectura']),
            models.Index(fields=['-fecha_lectura', '-hora_lectura']),
            models.Index(fields=['id_Lectura', 'turno']),
            models.Index(fields=['-fecha_lectura', 'turno']),
        ]

    def __str__(self):
        bovino_nombre = self.id_Lectura.id_Bovino.nombre if self.id_Lectura else 'Sin bovino'
        turno_display = dict(self.TURNO_CHOICES).get(self.turno, self.turno)
        return f"{bovino_nombre} - {self.fecha_lectura} {turno_display} - {self.estado_salud}"

    def hora_lectura_guayaquil(self):
        """Retorna la hora de lectura (ya está en zona horaria de Guayaquil)"""
        return str(self.hora_lectura)
    
    hora_lectura_guayaquil.short_description = 'Hora (Guayaquil)'

    def save(self, *args, **kwargs):
        """
        Calcula automáticamente el estado de salud según la temperatura para vacas lecheras.
        Si hay temperatura disponible (de sensor o manual), determina el estado.
        """
        # Si hay temperatura disponible, calcular estado_salud automáticamente
        if self.temperatura is not None:
            # Rangos específicos para vacas lecheras (bovinos adultos)
            # Normal: 38-39°C
            # Alerta: 36-38°C o 39-40°C
            # Crítico: <36°C (hipotermia) o >40°C (fiebre alta)
            if self.temperatura < 36:
                self.estado_salud = 'Crítico'  # Hipotermia
            elif 36 <= self.temperatura < 38:
                self.estado_salud = 'Alerta'  # Temperatura baja
            elif 38 <= self.temperatura <= 39:
                self.estado_salud = 'Normal'  # Rango normal
            elif 39 < self.temperatura <= 40:
                self.estado_salud = 'Alerta'  # Fiebre leve
            else:  # temperatura > 40
                self.estado_salud = 'Crítico'  # Fiebre alta
        
        super().save(*args, **kwargs)