from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Usuario, Paciente, Medico, Especialidad, Turno, HorarioAtencion, ObraSocial
from .utils import es_dia_laboral, es_feriado
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
            'data-allow-past': 'true',
            'max': date.today().isoformat()
        })
    )
    
    def clean_fecha_nacimiento(self):
        fecha_nac = self.cleaned_data.get('fecha_nacimiento')
        
        if fecha_nac:
            # Validar que no sea fecha futura
            if fecha_nac > date.today():
                raise forms.ValidationError('La fecha de nacimiento no puede ser posterior a la fecha actual. Por favor, ingrese una fecha de nacimiento válida.')
            
            # Validar edad mínima (18 años)
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            
            if edad < 18:
                raise forms.ValidationError('Debe tener al menos 18 años para registrarse y solicitar turnos de forma autónoma. Si es menor de edad, debe asistir con un adulto responsable.')
        
        return fecha_nac
    
    obra_social_obj = forms.ModelChoiceField(
        queryset=ObraSocial.objects.filter(activo=True),
        required=False,
        label='Obra Social',
        empty_label='Particular (sin obra social)',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
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
                obra_social_obj=self.cleaned_data.get('obra_social_obj'),
                numero_afiliado=self.cleaned_data.get('numero_afiliado', '')
            )
        return user


class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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


class AsignarMedicoRolForm(forms.ModelForm):
    """Formulario simplificado para asignar rol de médico (sin biografía ni foto)"""
    class Meta:
        model = Medico
        fields = ['especialidades', 'matricula', 'activo']
        widgets = {
            'especialidades': forms.CheckboxSelectMultiple(),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AsignarMedicoForm(forms.Form):
    """Formulario para buscar y asignar rol de médico a usuario existente"""
    buscar = forms.CharField(
        max_length=100,
        required=False,
        label='Buscar usuario por nombre, apellido, email o DNI',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese nombre, apellido, email o DNI...'
        })
    )
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),
        required=False,
        label='Seleccionar Usuario',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='-- Seleccione un usuario --'
    )
    
    def __init__(self, *args, **kwargs):
        busqueda = kwargs.pop('busqueda', None)
        super().__init__(*args, **kwargs)
        
        # Solo mostrar usuarios que no sean médicos ni admins
        queryset = Usuario.objects.filter(rol='paciente')
        
        if busqueda:
            # Filtrar por búsqueda
            queryset = queryset.filter(
                Q(first_name__icontains=busqueda) |
                Q(last_name__icontains=busqueda) |
                Q(email__icontains=busqueda) |
                Q(dni__icontains=busqueda) |
                Q(username__icontains=busqueda)
            )
        
        self.fields['usuario'].queryset = queryset
        
        # Personalizar la representación del usuario
        self.fields['usuario'].label_from_instance = lambda obj: f"{obj.get_full_name()} - {obj.email} (DNI: {obj.dni})"


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
        
        # Validar que no sea feriado ni fin de semana
        if fecha:
            es_laboral, mensaje = es_dia_laboral(fecha)
            if not es_laboral:
                raise forms.ValidationError(mensaje)
        
        # Validar conflicto de horarios (solo con turnos activos si es pendiente)
        if fecha and hora and medico:
            estado_actual = cleaned_data.get('estado')
            
            # Si el turno es pendiente, solo validar contra activos/en_atencion
            # Si el turno es activo, validar también contra pendientes
            if estado_actual == 'pendiente':
                estados_a_validar = ['activo', 'en_atencion']
            else:
                estados_a_validar = ['pendiente', 'activo', 'en_atencion']
            
            turno_existente = Turno.objects.filter(
                medico=medico,
                fecha=fecha,
                hora=hora,
                estado__in=estados_a_validar
            )
            
            # Si estamos editando, excluir el turno actual
            if self.instance.pk:
                turno_existente = turno_existente.exclude(pk=self.instance.pk)
            
            if turno_existente.exists():
                if estado_actual == 'pendiente':
                    raise forms.ValidationError('Ya existe un turno activo para este médico en ese horario.')
                else:
                    raise forms.ValidationError('Ya existe un turno para este médico en ese horario.')
        
        return cleaned_data


class PacienteTurnoForm(forms.ModelForm):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.filter(activo=True),
        label='Especialidad',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_especialidad'})
    )
    medico_busqueda = forms.CharField(
        required=False,
        label='Buscar Médico (Opcional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_medico_busqueda',
            'placeholder': 'Buscar médico por nombre...',
            'autocomplete': 'off'
        })
    )
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.filter(activo=True),
        label='Médico',
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_medico'})
    )
    
    class Meta:
        model = Turno
        fields = ['especialidad', 'medico', 'fecha', 'hora', 'motivo_consulta']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date', 
                'id': 'id_fecha',
                'min': date.today().isoformat()
            }),
            'hora': forms.Select(attrs={'class': 'form-control', 'id': 'id_hora'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'}),
        }
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        
        if fecha:
            # Validar que no sea fecha pasada
            if fecha < datetime.now().date():
                raise forms.ValidationError('No se pueden solicitar turnos en fechas pasadas.')
            
            # Validar que no sea feriado ni fin de semana
            es_laboral, mensaje = es_dia_laboral(fecha)
            if not es_laboral:
                raise forms.ValidationError(mensaje)
        
        return fecha
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        medico = cleaned_data.get('medico')
        
        # Validar que NO haya turnos activos (pero permitir pendientes)
        if fecha and hora and medico:
            turno_activo_existente = Turno.objects.filter(
                medico=medico,
                fecha=fecha,
                hora=hora,
                estado__in=['activo', 'en_atencion']
            )
            
            if turno_activo_existente.exists():
                raise forms.ValidationError(
                    f'Lo sentimos, el horario {hora.strftime("%H:%M")} ya no está disponible para este médico. '
                    'Por favor, seleccione otro horario.'
                )
        
        return cleaned_data


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
        fields = ['obra_social_obj', 'numero_afiliado', 'observaciones']
        widgets = {
            'obra_social_obj': forms.Select(attrs={'class': 'form-control'}),
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
        
        # Configurar obra social
        self.fields['obra_social_obj'].label = 'Obra Social'
        self.fields['obra_social_obj'].empty_label = 'Particular (sin obra social)'
        self.fields['obra_social_obj'].queryset = ObraSocial.objects.filter(activo=True)