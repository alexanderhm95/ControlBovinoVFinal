"""
Formularios del sistema de Control Bovino
Define formularios para gestión de usuarios y perfiles
"""

from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from .models import PersonalInfo


# Validadores personalizados
cedula_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='La cédula debe contener exactamente 10 dígitos.'
)

telefono_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='El teléfono debe contener exactamente 10 dígitos.'
)


class PersonalInfoForm(forms.ModelForm):
    """
    Formulario para crear/editar información personal de usuarios
    Incluye validaciones y widgets personalizados
    """
    
    class Meta:
        model = PersonalInfo
        fields = ['cedula', 'telefono', 'nombre', 'apellido', 'email']
        labels = {
            'cedula': 'Cédula',
            'telefono': 'Teléfono',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
        }
        help_texts = {
            'cedula': '10 dígitos sin guiones ni espacios',
            'telefono': '10 dígitos sin guiones ni espacios',
            'nombre': 'Ingrese su(s) nombre(s)',
            'apellido': 'Ingrese su(s) apellido(s)',
            'email': 'Este será su nombre de usuario para iniciar sesión',
        }
        widgets = {
            'cedula': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Ej: 1234567890',
                'maxlength': '10',
                'pattern': r'\d{10}'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Ej: 0987654321',
                'maxlength': '10',
                'pattern': r'\d{10}'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Ingrese nombre(s)',
                'maxlength': '50'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Ingrese apellido(s)',
                'maxlength': '50'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': 'correo@ejemplo.com',
                'maxlength': '100'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)
        
        # Agregar validadores personalizados
        self.fields['cedula'].validators.append(cedula_validator)
        self.fields['telefono'].validators.append(telefono_validator)
        
        # Asegurar que todos los campos tengan la clase 'input'
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'input'
            field.widget.attrs['required'] = 'required'

    def clean_cedula(self):
        """Validación adicional para cédula"""
        cedula = self.cleaned_data.get('cedula')
        if cedula:
            cedula = cedula.strip()
            if not cedula.isdigit():
                raise forms.ValidationError('La cédula debe contener solo números.')
            if len(cedula) != 10:
                raise forms.ValidationError('La cédula debe tener exactamente 10 dígitos.')
        return cedula

    def clean_telefono(self):
        """Validación adicional para teléfono"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono = telefono.strip()
            if not telefono.isdigit():
                raise forms.ValidationError('El teléfono debe contener solo números.')
            if len(telefono) != 10:
                raise forms.ValidationError('El teléfono debe tener exactamente 10 dígitos.')
        return telefono

    def clean_email(self):
        """Validación adicional para email"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            # Verificar si ya existe (excepto en modo edición)
            if self.instance.pk is None:  # Solo en modo creación
                if PersonalInfo.objects.filter(email=email).exists():
                    raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return email


class EditPersonalInfoForm(forms.ModelForm):
    """
    Formulario para editar información personal existente
    Similar a PersonalInfoForm pero permite actualizaciones
    """
    
    class Meta:
        model = PersonalInfo
        fields = ['cedula', 'telefono', 'nombre', 'apellido', 'email']
        labels = {
            'cedula': 'Cédula',
            'telefono': 'Teléfono',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
        }
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'input', 'maxlength': '10'}),
            'telefono': forms.TextInput(attrs={'class': 'input', 'maxlength': '10'}),
            'nombre': forms.TextInput(attrs={'class': 'input', 'maxlength': '50'}),
            'apellido': forms.TextInput(attrs={'class': 'input', 'maxlength': '50'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'maxlength': '100'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditPersonalInfoForm, self).__init__(*args, **kwargs)
        self.fields['cedula'].validators.append(cedula_validator)
        self.fields['telefono'].validators.append(telefono_validator)


class EditUserForm(forms.ModelForm):
    """
    Formulario para editar permisos de usuario (is_staff)
    """
    is_staff = forms.BooleanField(
        required=False,
        label='Usuario Staff',
        help_text='Los usuarios staff tienen acceso al panel de administración'
    )

    class Meta:
        model = User
        fields = ['is_staff']


class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulario personalizado para recuperación de contraseña
    Valida que el email exista en la base de datos
    """
    
    def clean_email(self):
        """Validar que el email esté registrado y activo"""
        email = self.cleaned_data['email'].lower().strip()
        
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'No hay ninguna cuenta asociada a este correo electrónico.'
            )
        
        # Verificar que el usuario esté activo
        user = User.objects.filter(email=email).first()
        if user and not user.is_active:
            raise forms.ValidationError(
                'Esta cuenta está desactivada. Contacte al administrador.'
            )
        
        return email