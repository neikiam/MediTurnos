from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Paciente, Medico, Especialidad, Turno, HorarioAtencion
from datetime import datetime, time, date

class RegistroPacienteForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Email')
    dni = forms.CharField(max_length=8, required=True, label='DNI')
    telefono = forms.CharField(max_length=15, required=True, label='Teléfono')
    fecha_nacimiento = forms.DateField(
        required=True, 
        label='Fecha de Nacimiento',
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'],
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'dd/mm/aaaa',
            'data-allow-past': 'true'
        })
    )
    obra_social = forms.CharField(max_length=100, required=False, label='Obra Social')
    numero_afiliado = forms.CharField(max_length=50, required=False, label='Número de Afiliado')
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'dni', 'telefono', 
                  'fecha_nacimiento', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'paciente'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.dni = self.cleaned_data['dni']
        user.telefono = self.cleaned_data['telefono']
        user.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        
        if commit:
            user.save()
            # Crear perfil de paciente
            Paciente.objects.create(
                usuario=user,
                obra_social=self.cleaned_data.get('obra_social', ''),
                numero_afiliado=self.cleaned_data.get('numero_afiliado', '')
            )
        return user


class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre', 'descripcion', 'duracion_turno', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duracion_turno': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MedicoUsuarioForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Email')
    dni = forms.CharField(max_length=8, required=True, label='DNI')
    telefono = forms.CharField(max_length=15, required=True, label='Teléfono')
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label='Contraseña (dejar en blanco para mantener la actual)'
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'dni', 'telefono']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['especialidades', 'matricula', 'biografia', 'foto', 'activo']
        widgets = {
            'especialidades': forms.CheckboxSelectMultiple(),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HorarioAtencionForm(forms.ModelForm):
    class Meta:
        model = HorarioAtencion
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        widgets = {
            'dia_semana': forms.Select(attrs={'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError('La hora de inicio debe ser anterior a la hora de fin.')
        
        # Validar horarios del consultorio (7:00 - 16:00)
        if hora_inicio and (hora_inicio < time(7, 0) or hora_inicio > time(16, 0)):
            raise forms.ValidationError('El horario debe estar entre 7:00 y 16:00.')
        
        if hora_fin and (hora_fin < time(7, 0) or hora_fin > time(16, 0)):
            raise forms.ValidationError('El horario debe estar entre 7:00 y 16:00.')
        
        return cleaned_data


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['paciente', 'medico', 'especialidad', 'fecha', 'hora', 'motivo_consulta', 'estado']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-control'}),
            'especialidad': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        medico = cleaned_data.get('medico')
        
        # Validar que no sea fecha pasada
        if fecha and fecha < datetime.now().date():
            raise forms.ValidationError('No se pueden crear turnos en fechas pasadas.')
        
        # Validar conflicto de horarios
        if fecha and hora and medico:
            turno_existente = Turno.objects.filter(
                medico=medico,
                fecha=fecha,
                hora=hora,
                estado__in=['pendiente', 'confirmado', 'en_atencion']
            )
            
            # Si estamos editando, excluir el turno actual
            if self.instance.pk:
                turno_existente = turno_existente.exclude(pk=self.instance.pk)
            
            if turno_existente.exists():
                raise forms.ValidationError('Ya existe un turno para este médico en ese horario.')
        
        return cleaned_data


class PacienteTurnoForm(forms.ModelForm):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.filter(activo=True),
        label='Especialidad',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_especialidad'})
    )
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.filter(activo=True),
        label='Médico',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_medico'})
    )
    
    class Meta:
        model = Turno
        fields = ['especialidad', 'medico', 'fecha', 'hora', 'motivo_consulta']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_fecha'}),
            'hora': forms.Select(attrs={'class': 'form-control', 'id': 'id_hora'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
        }


class AtenderTurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['estado', 'notas_medico']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas_medico': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo permitir ciertos estados para el médico
        self.fields['estado'].choices = [
            ('en_atencion', 'En Atención'),
            ('atendido', 'Atendido'),
            ('ausente', 'Ausente'),
            ('cancelado_medico', 'Cancelado por Médico'),
        ]


class PerfilPacienteForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Email')
    telefono = forms.CharField(max_length=15, required=True, label='Teléfono')
    direccion = forms.CharField(max_length=200, required=False, label='Dirección')
    
    class Meta:
        model = Paciente
        fields = ['obra_social', 'numero_afiliado', 'observaciones']
        widgets = {
            'obra_social': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_afiliado': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.usuario:
            self.fields['first_name'].initial = self.instance.usuario.first_name
            self.fields['last_name'].initial = self.instance.usuario.last_name
            self.fields['email'].initial = self.instance.usuario.email
            self.fields['telefono'].initial = self.instance.usuario.telefono
            self.fields['direccion'].initial = self.instance.usuario.direccion