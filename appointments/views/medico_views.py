"""
Vistas del panel de médico
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count
from datetime import datetime, timedelta
import calendar

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
    ahora = timezone.now()
    
    # Turnos de hoy (solo activos y en proceso)
    turnos_hoy = Turno.objects.filter(
        medico=medico,
        fecha=hoy,
        estado__in=['activo', 'en_atencion', 'atendido']
    ).select_related('paciente__usuario', 'especialidad').order_by('hora')
    
    # Agregar información de si cada turno ya pasó
    for turno in turnos_hoy:
        fecha_hora_turno = timezone.make_aware(datetime.combine(turno.fecha, turno.hora))
        turno.ya_paso = fecha_hora_turno <= ahora
    
    # Próximos turnos (solo activos)
    proximos_turnos = Turno.objects.filter(
        medico=medico,
        fecha__gt=hoy,
        estado='activo'
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
    """Agenda del médico con calendario mensual"""
    if request.user.rol != 'medico':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    medico = request.user.perfil_medico
    hoy = timezone.now().date()
    
    # Obtener mes y año de los parámetros, o usar mes actual
    mes = int(request.GET.get('mes', hoy.month))
    año = int(request.GET.get('año', hoy.year))
    
    # Validar mes y año
    if mes < 1 or mes > 12:
        mes = hoy.month
    if año < 2020 or año > 2030:
        año = hoy.year
    
    # Fecha seleccionada para mostrar turnos
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except:
            fecha_seleccionada = hoy
    else:
        fecha_seleccionada = hoy
    
    # Obtener primer y último día del mes
    primer_dia = datetime(año, mes, 1).date()
    ultimo_dia = datetime(año, mes, calendar.monthrange(año, mes)[1]).date()
    
    # Contar turnos por día del mes
    turnos_por_dia = Turno.objects.filter(
        medico=medico,
        fecha__gte=primer_dia,
        fecha__lte=ultimo_dia,
        estado__in=['activo', 'en_atencion', 'atendido', 'ausente']
    ).values('fecha').annotate(total=Count('id'))
    
    # Crear diccionario con conteo de turnos por fecha
    conteo_turnos = {item['fecha']: item['total'] for item in turnos_por_dia}
    
    # Generar estructura del calendario
    cal = calendar.monthcalendar(año, mes)
    
    # Enriquecer el calendario con el conteo de turnos
    calendario_con_turnos = []
    for semana in cal:
        semana_datos = []
        for dia in semana:
            if dia == 0:
                semana_datos.append({'dia': 0, 'turnos': 0, 'fecha': None})
            else:
                fecha_dia = datetime(año, mes, dia).date()
                num_turnos = conteo_turnos.get(fecha_dia, 0)
                semana_datos.append({
                    'dia': dia,
                    'turnos': num_turnos,
                    'fecha': fecha_dia,
                    'es_hoy': fecha_dia == hoy,
                    'es_pasado': fecha_dia < hoy,
                    'es_seleccionado': fecha_dia == fecha_seleccionada
                })
        calendario_con_turnos.append(semana_datos)
    
    # Turnos del día seleccionado
    turnos = Turno.objects.filter(
        medico=medico,
        fecha=fecha_seleccionada,
        estado__in=['activo', 'en_atencion', 'atendido', 'ausente']
    ).select_related('paciente__usuario', 'especialidad').order_by('hora')
    
    # Agregar información de si cada turno ya pasó
    ahora = timezone.now()
    for turno in turnos:
        fecha_hora_turno = timezone.make_aware(datetime.combine(turno.fecha, turno.hora))
        turno.ya_paso = fecha_hora_turno <= ahora
    
    # Calcular mes anterior y siguiente
    if mes == 1:
        mes_anterior, año_anterior = 12, año - 1
    else:
        mes_anterior, año_anterior = mes - 1, año
    
    if mes == 12:
        mes_siguiente, año_siguiente = 1, año + 1
    else:
        mes_siguiente, año_siguiente = mes + 1, año
    
    # Nombres de meses en español
    meses_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    context = {
        'medico': medico,
        'calendario': calendario_con_turnos,
        'mes': mes,
        'año': año,
        'mes_nombre': meses_es[mes - 1],
        'mes_anterior': mes_anterior,
        'año_anterior': año_anterior,
        'mes_siguiente': mes_siguiente,
        'año_siguiente': año_siguiente,
        'fecha_seleccionada': fecha_seleccionada,
        'turnos': turnos,
        'hoy': hoy,
    }
    return render(request, 'appointments/medico/agenda.html', context)


@login_required
def medico_atender_turno(request, pk):
    """Atender turno"""
    if request.user.rol != 'medico':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    turno = get_object_or_404(Turno, pk=pk, medico=request.user.perfil_medico)
    
    # Verificar que la fecha y hora del turno ya hayan pasado
    ahora = timezone.now()
    fecha_hora_turno = timezone.make_aware(datetime.combine(turno.fecha, turno.hora))
    turno_ya_paso = fecha_hora_turno <= ahora
    
    # Solo permitir modificar el estado si el turno ya pasó
    if request.method == 'POST':
        if not turno_ya_paso:
            messages.error(request, 'No puedes atender un turno que aún no ha llegado. Espera a que llegue la fecha y hora programada.')
            return redirect('medico_agenda')
        
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
        'turno_ya_paso': turno_ya_paso,
        'fecha_hora_turno': fecha_hora_turno,
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
