"""
Vistas del panel de paciente
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from ..models import Turno
from ..forms import PacienteTurnoForm, PerfilPacienteForm


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
