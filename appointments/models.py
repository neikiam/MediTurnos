from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import time

# Modelo de Usuario Personalizado
class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('medico', 'Médico'),
        ('paciente', 'Paciente'),
    )
    
    rol = models.CharField(max_length=10, choices=ROLES, default='paciente')
    dni = models.CharField(max_length=8, unique=True, validators=[
        RegexValidator(r'^\d{7,8}$', 'Ingrese un DNI válido (7-8 dígitos)')
    ])
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"


# Modelo de Especialidad
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    duracion_turno = models.IntegerField(default=30, help_text="Duración en minutos")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# Modelo de Médico (Perfil extendido)
class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_medico')
    especialidades = models.ManyToManyField(Especialidad, related_name='medicos')
    matricula = models.CharField(max_length=20, unique=True)
    biografia = models.TextField(blank=True)
    foto = models.ImageField(upload_to='medicos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['usuario__last_name', 'usuario__first_name']
    
    def __str__(self):
        return f"Dr/a. {self.usuario.get_full_name()}"
    
    def get_especialidades_str(self):
        return ", ".join([esp.nombre for esp in self.especialidades.all()])


# Modelo de Horario de Atención
class HorarioAtencion(models.Model):
    DIAS_SEMANA = (
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    )
    
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Horario de Atención'
        verbose_name_plural = 'Horarios de Atención'
        unique_together = ['medico', 'dia_semana', 'hora_inicio']
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.medico} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


# Modelo de Paciente (Perfil extendido)
class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_paciente')
    obra_social = models.CharField(max_length=100, blank=True)
    numero_afiliado = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['usuario__last_name', 'usuario__first_name']
    
    def __str__(self):
        return self.usuario.get_full_name()


# Modelo de Turno
class Turno(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_atencion', 'En Atención'),
        ('atendido', 'Atendido'),
        ('cancelado_paciente', 'Cancelado por Paciente'),
        ('cancelado_medico', 'Cancelado por Médico'),
        ('ausente', 'Ausente'),
    )
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='turnos')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='turnos')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo_consulta = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    notas_medico = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['-fecha', '-hora']
        unique_together = ['medico', 'fecha', 'hora']
    
    def __str__(self):
        return f"{self.paciente} - {self.medico} - {self.fecha} {self.hora}"
    
    def get_estado_color(self):
        colores = {
            'pendiente': 'warning',
            'confirmado': 'info',
            'en_atencion': 'primary',
            'atendido': 'success',
            'cancelado_paciente': 'secondary',
            'cancelado_medico': 'danger',
            'ausente': 'dark',
        }
        return colores.get(self.estado, 'secondary')
    
    def puede_cancelar(self):
        """Verifica si el turno puede ser cancelado"""
        if self.estado in ['atendido', 'cancelado_paciente', 'cancelado_medico', 'ausente']:
            return False
        # No permitir cancelar turnos con menos de 2 horas de anticipación
        ahora = timezone.now()
        turno_datetime = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.hora)
        )
        return turno_datetime > ahora + timezone.timedelta(hours=2)


# Modelo de Configuración del Sistema
class ConfiguracionSistema(models.Model):
    nombre_consultorio = models.CharField(max_length=200, default="MediTurnos")
    direccion = models.CharField(max_length=300, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    horario_apertura = models.TimeField(default=time(7, 0))
    horario_cierre = models.TimeField(default=time(16, 0))
    turnos_simultaneos = models.IntegerField(default=1, help_text="Turnos simultáneos por médico")
    cancelacion_horas_minimas = models.IntegerField(default=2, help_text="Horas mínimas para cancelar")
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuración del Sistema'
    
    def __str__(self):
        return self.nombre_consultorio
    
    @classmethod
    def get_configuracion(cls):
        config, created = cls.objects.get_or_create(pk=1)
        return config