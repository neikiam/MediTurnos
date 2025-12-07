"""
Vistas del panel de administrador
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from ..models import (
    Usuario, Paciente, Medico, Especialidad, Turno,
    HorarioAtencion
)
from ..forms import (
    EspecialidadForm, MedicoUsuarioForm, MedicoForm,
    HorarioAtencionForm, TurnoForm
)

@login_required
def admin_dashboard(request):
    """Dashboard principal del administrador"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard')
    
    # Estadísticas generales
    total_pacientes = Paciente.objects.count()
    total_medicos = Medico.objects.filter(activo=True).count()
    total_especialidades = Especialidad.objects.filter(activo=True).count()
    
    # Turnos de hoy
    hoy = timezone.now().date()
    turnos_hoy = Turno.objects.filter(fecha=hoy).count()
    turnos_pendientes = Turno.objects.filter(fecha=hoy, estado='pendiente').count()
    turnos_atendidos = Turno.objects.filter(fecha=hoy, estado='atendido').count()
    
    # Últimos turnos
    ultimos_turnos = Turno.objects.select_related(
        'paciente__usuario', 'medico__usuario', 'especialidad'
    ).order_by('-fecha_creacion')[:10]
    
    context = {
        'total_pacientes': total_pacientes,
        'total_medicos': total_medicos,
        'total_especialidades': total_especialidades,
        'turnos_hoy': turnos_hoy,
        'turnos_pendientes': turnos_pendientes,
        'turnos_atendidos': turnos_atendidos,
        'ultimos_turnos': ultimos_turnos,
    }
    return render(request, 'appointments/admin/dashboard.html', context)


# --- Gestión de Especialidades ---

@login_required
def admin_especialidades(request):
    """Lista de especialidades"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    especialidades = Especialidad.objects.all().order_by('nombre')
    return render(request, 'appointments/admin/especialidades.html', {'especialidades': especialidades})


@login_required
def admin_especialidad_crear(request):
    """Crear nueva especialidad"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialidad creada correctamente.')
            return redirect('admin_especialidades')
    else:
        form = EspecialidadForm()
    
    return render(request, 'appointments/admin/especialidad_form.html', {'form': form, 'accion': 'Crear'})


@login_required
def admin_especialidad_editar(request, pk):
    """Editar especialidad"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    especialidad = get_object_or_404(Especialidad, pk=pk)
    
    if request.method == 'POST':
        form = EspecialidadForm(request.POST, instance=especialidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialidad actualizada correctamente.')
            return redirect('admin_especialidades')
    else:
        form = EspecialidadForm(instance=especialidad)
    
    return render(request, 'appointments/admin/especialidad_form.html', {'form': form, 'accion': 'Editar'})


@login_required
def admin_especialidad_eliminar(request, pk):
    """Eliminar especialidad"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    especialidad = get_object_or_404(Especialidad, pk=pk)
    
    if request.method == 'POST':
        especialidad.delete()
        messages.success(request, 'Especialidad eliminada correctamente.')
        return redirect('admin_especialidades')
    
    return render(request, 'appointments/admin/especialidad_eliminar.html', {'especialidad': especialidad})


# --- Gestión de Médicos ---

@login_required
def admin_medicos(request):
    """Lista de médicos"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    medicos = Medico.objects.select_related('usuario').prefetch_related('especialidades').all()
    return render(request, 'appointments/admin/medicos.html', {'medicos': medicos})


@login_required
def admin_medico_crear(request):
    """Crear nuevo médico"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        user_form = MedicoUsuarioForm(request.POST)
        medico_form = MedicoForm(request.POST, request.FILES)
        
        if user_form.is_valid() and medico_form.is_valid():
            # Crear usuario
            user = user_form.save(commit=False)
            user.rol = 'medico'
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                user.set_password('medico123')  # Contraseña por defecto
            user.save()
            
            # Crear perfil de médico
            medico = medico_form.save(commit=False)
            medico.usuario = user
            medico.save()
            medico_form.save_m2m()  # Guardar relaciones ManyToMany
            
            messages.success(request, f'Médico {user.get_full_name()} creado correctamente.')
            return redirect('admin_medicos')
    else:
        user_form = MedicoUsuarioForm()
        medico_form = MedicoForm()
    
    context = {
        'user_form': user_form,
        'medico_form': medico_form,
        'accion': 'Crear'
    }
    return render(request, 'appointments/admin/medico_form.html', context)


@login_required
def admin_medico_editar(request, pk):
    """Editar médico"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    medico = get_object_or_404(Medico, pk=pk)
    
    if request.method == 'POST':
        user_form = MedicoUsuarioForm(request.POST, instance=medico.usuario)
        medico_form = MedicoForm(request.POST, request.FILES, instance=medico)
        
        if user_form.is_valid() and medico_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
            medico_form.save()
            
            messages.success(request, 'Médico actualizado correctamente.')
            return redirect('admin_medicos')
    else:
        user_form = MedicoUsuarioForm(instance=medico.usuario)
        medico_form = MedicoForm(instance=medico)
    
    context = {
        'user_form': user_form,
        'medico_form': medico_form,
        'accion': 'Editar',
        'medico': medico
    }
    return render(request, 'appointments/admin/medico_form.html', context)


@login_required
def admin_medico_eliminar(request, pk):
    """Eliminar médico"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    medico = get_object_or_404(Medico, pk=pk)
    
    if request.method == 'POST':
        usuario = medico.usuario
        medico.delete()
        usuario.delete()
        messages.success(request, 'Médico eliminado correctamente.')
        return redirect('admin_medicos')
    
    return render(request, 'appointments/admin/medico_eliminar.html', {'medico': medico})


@login_required
def admin_medico_horarios(request, pk):
    """Gestionar horarios de atención de un médico"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    medico = get_object_or_404(Medico, pk=pk)
    horarios = medico.horarios.all().order_by('dia_semana', 'hora_inicio')
    
    if request.method == 'POST':
        form = HorarioAtencionForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.medico = medico
            horario.save()
            messages.success(request, 'Horario agregado correctamente.')
            return redirect('admin_medico_horarios', pk=pk)
    else:
        form = HorarioAtencionForm()
    
    context = {
        'medico': medico,
        'horarios': horarios,
        'form': form,
    }
    return render(request, 'appointments/admin/medico_horarios.html', context)


# --- Gestión de Pacientes ---

@login_required
def admin_pacientes(request):
    """Lista de pacientes"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    pacientes = Paciente.objects.select_related('usuario').all()
    return render(request, 'appointments/admin/pacientes.html', {'pacientes': pacientes})


@login_required
def admin_paciente_ver(request, pk):
    """Ver detalles de un paciente"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    paciente = get_object_or_404(Paciente, pk=pk)
    turnos = paciente.turnos.select_related('medico__usuario', 'especialidad').order_by('-fecha')
    
    context = {
        'paciente': paciente,
        'turnos': turnos,
    }
    return render(request, 'appointments/admin/paciente_ver.html', context)


# --- Gestión de Turnos (Admin) ---

@login_required
def admin_turnos(request):
    """Lista de turnos"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    estado = request.GET.get('estado')
    medico_id = request.GET.get('medico')
    
    turnos = Turno.objects.select_related(
        'paciente__usuario', 'medico__usuario', 'especialidad'
    ).all()
    
    if fecha_desde:
        turnos = turnos.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        turnos = turnos.filter(fecha__lte=fecha_hasta)
    if estado:
        turnos = turnos.filter(estado=estado)
    if medico_id:
        turnos = turnos.filter(medico_id=medico_id)
    
    turnos = turnos.order_by('-fecha', '-hora')
    
    medicos = Medico.objects.filter(activo=True).select_related('usuario')
    
    context = {
        'turnos': turnos,
        'medicos': medicos,
        'estados': Turno.ESTADOS,
    }
    return render(request, 'appointments/admin/turnos.html', context)


@login_required
def admin_turno_crear(request):
    """Crear nuevo turno"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turno creado correctamente.')
            return redirect('admin_turnos')
    else:
        form = TurnoForm()
    
    return render(request, 'appointments/admin/turno_form.html', {'form': form, 'accion': 'Crear'})


@login_required
def admin_turno_editar(request, pk):
    """Editar turno"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    turno = get_object_or_404(Turno, pk=pk)
    
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turno actualizado correctamente.')
            return redirect('admin_turnos')
    else:
        form = TurnoForm(instance=turno)
    
    return render(request, 'appointments/admin/turno_form.html', {'form': form, 'accion': 'Editar', 'turno': turno})


@login_required
def admin_turno_eliminar(request, pk):
    """Eliminar turno"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    turno = get_object_or_404(Turno, pk=pk)
    
    if request.method == 'POST':
        turno.delete()
        messages.success(request, 'Turno eliminado correctamente.')
        return redirect('admin_turnos')
    
    return render(request, 'appointments/admin/turno_eliminar.html', {'turno': turno})


# --- Estadísticas ---

@login_required
def admin_estadisticas(request):
    """Estadísticas del sistema"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    # Turnos por estado
    turnos_por_estado = Turno.objects.values('estado').annotate(total=Count('id'))
    
    # Turnos por especialidad
    turnos_por_especialidad = Turno.objects.values(
        'especialidad__nombre'
    ).annotate(total=Count('id')).order_by('-total')
    
    # Médicos más solicitados
    medicos_populares = Turno.objects.values(
        'medico__usuario__first_name', 'medico__usuario__last_name'
    ).annotate(total=Count('id')).order_by('-total')[:5]
    
    # Turnos por mes (últimos 6 meses)
    desde = timezone.now().date() - timedelta(days=180)
    turnos_por_mes = Turno.objects.filter(
        fecha__gte=desde
    ).extra(
        select={'mes': "strftime('%%Y-%%m', fecha)"}
    ).values('mes').annotate(total=Count('id')).order_by('mes')
    
    context = {
        'turnos_por_estado': turnos_por_estado,
        'turnos_por_especialidad': turnos_por_especialidad,
        'medicos_populares': medicos_populares,
        'turnos_por_mes': turnos_por_mes,
    }
    return render(request, 'appointments/admin/estadisticas.html', context)


# ============================================
# VISTAS DE MÉDICO
# ============================================

@login_required
def medico_dashboard(request):
    """Dashboard del médico"""
    if request.user.rol != 'medico':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    medico = request.user.perfil_medico
    hoy = timezone.now().date()
    
    # Turnos de hoy
    turnos_hoy = Turno.objects.filter(
        medico=medico,
        fecha=hoy
    ).select_related('paciente__usuario', 'especialidad').order_by('hora')
    
    # Próximos turnos
    proximos_turnos = Turno.objects.filter(
        medico=medico,
        fecha__gt=hoy,
        estado__in=['pendiente', 'confirmado']
    ).select_related('paciente__usuario', 'especialidad').order_by('fecha', 'hora')[:5]
    
    # Estadísticas
    total_turnos_mes = Turno.objects.filter(
        medico=medico,
        fecha__month=hoy.month,
        fecha__year=hoy.year
    ).count()
    
    turnos_atendidos_mes = Turno.objects.filter(
        medico=medico,
        fecha__month=hoy.month,
        fecha__year=hoy.year,
        estado='atendido'
    ).count()
    
    context = {
        'medico': medico,
        'turnos_hoy': turnos_hoy,
        'proximos_turnos': proximos_turnos,
        'total_turnos_mes': total_turnos_mes,
        'turnos_atendidos_mes': turnos_atendidos_mes,
    }
    return render(request, 'appointments/medico/dashboard.html', context)


@login_required
def medico_agenda(request):
    """Agenda del médico"""
    if request.user.rol != 'medico':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    medico = request.user.perfil_medico
    
    # Filtro por fecha
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except:
            fecha = timezone.now().date()
    else:
        fecha = timezone.now().date()
    
    # Turnos del día seleccionado
    turnos = Turno.objects.filter(
        medico=medico,
        fecha=fecha
    ).select_related('paciente__usuario', 'especialidad').order_by('hora')
    
    context = {
        'medico': medico,
        'turnos': turnos,
        'fecha': fecha,
    }
    return render(request, 'appointments/medico/agenda.html', context)


@login_required
def medico_atender_turno(request, pk):
    """Atender turno"""
    if request.user.rol != 'medico':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    turno = get_object_or_404(Turno, pk=pk, medico=request.user.perfil_medico)
    
    if request.method == 'POST':
        form = AtenderTurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turno actualizado correctamente.')
            return redirect('medico_agenda')
    else:
        form = AtenderTurnoForm(instance=turno)
    
    context = {
        'turno': turno,
        'form': form,
    }
    return render(request, 'appointments/medico/atender_turno.html', context)


@login_required
def medico_perfil(request):
    """Perfil del médico"""
    if request.user.rol != 'medico':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    medico = request.user.perfil_medico
    horarios = medico.horarios.filter(activo=True).order_by('dia_semana', 'hora_inicio')
    
    context = {
        'medico': medico,
        'horarios': horarios,
    }
    return render(request, 'appointments/medico/perfil.html', context)


# ============================================
# VISTAS DE PACIENTE
# ============================================

@login_required
def paciente_dashboard(request):
    """Dashboard del paciente"""
    if request.user.rol != 'paciente':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    paciente = request.user.perfil_paciente
    hoy = timezone.now().date()
    
    # Próximos turnos
    proximos_turnos = Turno.objects.filter(
        paciente=paciente,
        fecha__gte=hoy,
        estado__in=['pendiente', 'confirmado']
    ).select_related('medico__usuario', 'especialidad').order_by('fecha', 'hora')[:5]
    
    # Historial de turnos
    historial_turnos = Turno.objects.filter(
        paciente=paciente,
        fecha__lt=hoy
    ).select_related('medico__usuario', 'especialidad').order_by('-fecha', '-hora')[:5]
    
    context = {
        'paciente': paciente,
        'proximos_turnos': proximos_turnos,
        'historial_turnos': historial_turnos,
    }
    return render(request, 'appointments/paciente/dashboard.html', context)


@login_required
def paciente_nuevo_turno(request):
    """Solicitar nuevo turno"""
    if request.user.rol != 'paciente':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    paciente = request.user.perfil_paciente
    
    if request.method == 'POST':
        form = PacienteTurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.paciente = paciente
            turno.estado = 'pendiente'
            turno.save()
            messages.success(request, 'Turno solicitado correctamente.')
            return redirect('paciente_mis_turnos')
    else:
        form = PacienteTurnoForm()
    
    return render(request, 'appointments/paciente/nuevo_turno.html', {'form': form})


@login_required
def paciente_mis_turnos(request):
    """Ver mis turnos"""
    if request.user.rol != 'paciente':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    paciente = request.user.perfil_paciente
    hoy = timezone.now().date()
    
    # Filtro
    filtro = request.GET.get('filtro', 'proximos')
    
    if filtro == 'proximos':
        turnos = Turno.objects.filter(
            paciente=paciente,
            fecha__gte=hoy
        ).select_related('medico__usuario', 'especialidad').order_by('fecha', 'hora')
    elif filtro == 'historial':
        turnos = Turno.objects.filter(
            paciente=paciente,
            fecha__lt=hoy
        ).select_related('medico__usuario', 'especialidad').order_by('-fecha', '-hora')
    else:
        turnos = Turno.objects.filter(
            paciente=paciente
        ).select_related('medico__usuario', 'especialidad').order_by('-fecha', '-hora')
    
    context = {
        'turnos': turnos,
        'filtro': filtro,
    }
    return render(request, 'appointments/paciente/mis_turnos.html', context)


@login_required
def paciente_cancelar_turno(request, pk):
    """Cancelar turno"""
    if request.user.rol != 'paciente':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    turno = get_object_or_404(Turno, pk=pk, paciente=request.user.perfil_paciente)
    
    if not turno.puede_cancelar():
        messages.error(request, 'No puedes cancelar este turno (estado actual o tiempo insuficiente).')
        return redirect('paciente_mis_turnos')
    
    if request.method == 'POST':
        turno.estado = 'cancelado_paciente'
        turno.save()
        messages.success(request, 'Turno cancelado correctamente.')
        return redirect('paciente_mis_turnos')
    
    return render(request, 'appointments/paciente/cancelar_turno.html', {'turno': turno})


@login_required
def paciente_perfil(request):
    """Perfil del paciente"""
    if request.user.rol != 'paciente':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    paciente = request.user.perfil_paciente
    
    if request.method == 'POST':
        form = PerfilPacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            # Actualizar usuario
            user = paciente.usuario
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.telefono = form.cleaned_data['telefono']
            user.direccion = form.cleaned_data['direccion']
            user.save()
            
            # Actualizar paciente
            form.save()
            
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('paciente_perfil')
    else:
        form = PerfilPacienteForm(instance=paciente)
    
    context = {
        'paciente': paciente,
        'form': form,
    }
    return render(request, 'appointments/paciente/perfil.html', context)


# ============================================
# API ENDPOINTS (AJAX)
# ============================================

@login_required
def api_medicos_por_especialidad(request, especialidad_id):
    """Obtener médicos por especialidad (AJAX)"""
    medicos = Medico.objects.filter(
        especialidades__id=especialidad_id,
        activo=True
    ).select_related('usuario')
    
    data = [
        {
            'id': medico.id,
            'nombre': str(medico)
        }
        for medico in medicos
    ]
    
    return JsonResponse(data, safe=False)


@login_required
def api_horarios_disponibles(request):
    """Obtener horarios disponibles para un médico en una fecha (AJAX)"""
    medico_id = request.GET.get('medico_id')
    fecha_str = request.GET.get('fecha')
    
    if not medico_id or not fecha_str:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    
    try:
        medico = Medico.objects.get(id=medico_id)
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except:
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)
    
    # Obtener día de la semana (0=Lunes, 6=Domingo)
    dia_semana = fecha.weekday()
    
    # Obtener horarios de atención del médico para ese día
    horarios_atencion = HorarioAtencion.objects.filter(
        medico=medico,
        dia_semana=dia_semana,
        activo=True
    )
    
    if not horarios_atencion.exists():
        return JsonResponse([], safe=False)
    
    # Generar slots de 30 minutos
    slots_disponibles = []
    
    for horario in horarios_atencion:
        hora_actual = horario.hora_inicio
        while hora_actual < horario.hora_fin:
            # Verificar si ya hay turno en ese horario
            turno_existente = Turno.objects.filter(
                medico=medico,
                fecha=fecha,
                hora=hora_actual,
                estado__in=['pendiente', 'confirmado', 'en_atencion']
            ).exists()
            
            if not turno_existente:
                slots_disponibles.append({
                    'hora': hora_actual.strftime('%H:%M'),
                    'disponible': True
                })
            
            # Incrementar 30 minutos
            hora_actual = (datetime.combine(fecha, hora_actual) + timedelta(minutes=30)).time()
    
    return JsonResponse(slots_disponibles, safe=False)
