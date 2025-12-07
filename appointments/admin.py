from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Paciente, Medico, Especialidad, 
    Turno, HorarioAtencion, ConfiguracionSistema
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'rol', 'is_active']
    list_filter = ['rol', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'dni']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'dni', 'telefono', 'direccion', 'fecha_nacimiento')
        }),
    )


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'duracion_turno', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_completo', 'matricula', 'get_especialidades', 'activo']
    list_filter = ['activo', 'especialidades']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'matricula']
    filter_horizontal = ['especialidades']
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre'
    
    def get_especialidades(self, obj):
        return ", ".join([e.nombre for e in obj.especialidades.all()])
    get_especialidades.short_description = 'Especialidades'


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_completo', 'obra_social', 'numero_afiliado']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'usuario__dni']
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre'


@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):
    list_display = ['medico', 'get_dia_semana_display', 'hora_inicio', 'hora_fin', 'activo']
    list_filter = ['dia_semana', 'activo']
    search_fields = ['medico__usuario__first_name', 'medico__usuario__last_name']


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'especialidad', 'fecha', 'hora', 'estado']
    list_filter = ['estado', 'fecha', 'especialidad']
    search_fields = ['paciente__usuario__first_name', 'medico__usuario__first_name']
    date_hierarchy = 'fecha'


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ['nombre_consultorio', 'horario_apertura', 'horario_cierre']
    
    def has_add_permission(self, request):
        # Solo permitir una configuración
        return not ConfiguracionSistema.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración
        return False