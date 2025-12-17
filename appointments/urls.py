from django.urls import path
from . import views
from .views import paciente_turnos_wizard

urlpatterns = [
    # Página de inicio
    path('', views.inicio, name='inicio'),
    
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_paciente, name='registro'),
    
    # Dashboard general
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # --- RUTAS DE ADMINISTRADOR ---
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # Gestión de Especialidades
    path('admin-panel/especialidades/', views.admin_especialidades, name='admin_especialidades'),
    path('admin-panel/especialidades/nueva/', views.admin_especialidad_crear, name='admin_especialidad_crear'),
    path('admin-panel/especialidades/<int:pk>/editar/', views.admin_especialidad_editar, name='admin_especialidad_editar'),
    path('admin-panel/especialidades/<int:pk>/eliminar/', views.admin_especialidad_eliminar, name='admin_especialidad_eliminar'),
    
    # Gestión de Médicos
    path('admin-panel/medicos/', views.admin_medicos, name='admin_medicos'),
    path('admin-panel/medicos/nuevo/', views.admin_medico_crear, name='admin_medico_crear'),
    path('admin-panel/medicos/<int:pk>/editar/', views.admin_medico_editar, name='admin_medico_editar'),
    path('admin-panel/medicos/<int:pk>/eliminar/', views.admin_medico_eliminar, name='admin_medico_eliminar'),
    path('admin-panel/medicos/<int:pk>/horarios/', views.admin_medico_horarios, name='admin_medico_horarios'),
    
    # Gestión de Pacientes
    path('admin-panel/pacientes/', views.admin_pacientes, name='admin_pacientes'),
    path('admin-panel/pacientes/<int:pk>/ver/', views.admin_paciente_ver, name='admin_paciente_ver'),
    
    # Gestión de Turnos (Admin)
    path('admin-panel/turnos/', views.admin_turnos, name='admin_turnos'),
    path('admin-panel/turnos/nuevo/', views.admin_turno_crear, name='admin_turno_crear'),
    path('admin-panel/turnos/<int:pk>/editar/', views.admin_turno_editar, name='admin_turno_editar'),
    path('admin-panel/turnos/<int:pk>/eliminar/', views.admin_turno_eliminar, name='admin_turno_eliminar'),
    path('admin-panel/turnos/<int:pk>/validar/', views.admin_turno_validar, name='admin_turno_validar'),
    path('admin-panel/turnos/<int:pk>/cambiar-estado/', views.admin_turno_cambiar_estado, name='admin_turno_cambiar_estado'),
    
    # Estadísticas
    path('admin-panel/estadisticas/', views.admin_estadisticas, name='admin_estadisticas'),
    
    # --- RUTAS DE MÉDICO ---
    path('medico-panel/', views.medico_dashboard, name='medico_dashboard'),
    path('medico-panel/agenda/', views.medico_agenda, name='medico_agenda'),
    path('medico-panel/turnos/<int:pk>/atender/', views.medico_atender_turno, name='medico_atender_turno'),
    path('medico-panel/perfil/', views.medico_perfil, name='medico_perfil'),
    
    # --- RUTAS DE PACIENTE ---
    path('paciente-panel/', views.paciente_dashboard, name='paciente_dashboard'),
    path('paciente-panel/nuevo-turno/', paciente_turnos_wizard.paciente_nuevo_turno_paso1, name='paciente_nuevo_turno'),
    path('paciente-panel/nuevo-turno/paso1/', paciente_turnos_wizard.paciente_nuevo_turno_paso1, name='paciente_nuevo_turno_paso1'),
    path('paciente-panel/nuevo-turno/paso2/', paciente_turnos_wizard.paciente_nuevo_turno_paso2, name='paciente_nuevo_turno_paso2'),
    path('paciente-panel/mis-turnos/', views.paciente_mis_turnos, name='paciente_mis_turnos'),
    path('paciente-panel/turnos/<int:pk>/cancelar/', views.paciente_cancelar_turno, name='paciente_cancelar_turno'),
    path('paciente-panel/perfil/', views.paciente_perfil, name='paciente_perfil'),
    
    # API endpoints (para obtener horarios disponibles en AJAX)
    path('api/medicos-por-especialidad/<int:especialidad_id>/', views.api_medicos_por_especialidad, name='api_medicos_por_especialidad'),
    path('api/horarios-disponibles/', views.api_horarios_disponibles, name='api_horarios_disponibles'),
    path('api/horarios-disponibles-especialidad/', paciente_turnos_wizard.api_horarios_disponibles_especialidad, name='api_horarios_disponibles_especialidad'),
]