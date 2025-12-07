"""
Vistas del panel de médico
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from ..models import Turno
from ..forms import AtenderTurnoForm


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
