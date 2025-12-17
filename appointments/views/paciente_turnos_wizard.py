"""
Vista mejorada de solicitud de turnos con flujo de 2 pasos
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import Turno, Especialidad, Medico, HorarioAtencion
from ..utils import es_dia_laboral


@login_required
def paciente_nuevo_turno_paso1(request):
    """Paso 1: Seleccionar especialidad y horario"""
    if request.user.rol != 'paciente':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        especialidad_id = request.POST.get('especialidad')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        
        if not all([especialidad_id, fecha, hora]):
            messages.error(request, 'Debe completar todos los campos.')
            return redirect('paciente_nuevo_turno_paso1')
        
        # Guardar en sesión para el paso 2
        request.session['turno_especialidad_id'] = especialidad_id
        request.session['turno_fecha'] = fecha
        request.session['turno_hora'] = hora
        
        return redirect('paciente_nuevo_turno_paso2')
    
    especialidades = Especialidad.objects.filter(activo=True)
    
    context = {
        'especialidades': especialidades,
        'fecha_minima': timezone.now().date().isoformat(),
    }
    return render(request, 'appointments/paciente/nuevo_turno_paso1.html', context)


@login_required
def paciente_nuevo_turno_paso2(request):
    """Paso 2: Seleccionar médico y motivo"""
    if request.user.rol != 'paciente':
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    # Recuperar datos del paso 1
    especialidad_id = request.session.get('turno_especialidad_id')
    fecha_str = request.session.get('turno_fecha')
    hora_str = request.session.get('turno_hora')
    
    if not all([especialidad_id, fecha_str, hora_str]):
        messages.error(request, 'Debe completar el paso 1 primero.')
        return redirect('paciente_nuevo_turno_paso1')
    
    try:
        especialidad = Especialidad.objects.get(id=especialidad_id)
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora = datetime.strptime(hora_str, '%H:%M').time()
    except:
        messages.error(request, 'Datos inválidos. Intente nuevamente.')
        return redirect('paciente_nuevo_turno_paso1')
    
    if request.method == 'POST':
        medico_id = request.POST.get('medico')
        motivo_consulta = request.POST.get('motivo_consulta', '')
        
        if not medico_id:
            messages.error(request, 'Debe seleccionar un médico.')
            return redirect('paciente_nuevo_turno_paso2')
        
        try:
            medico = Medico.objects.get(id=medico_id, especialidades=especialidad, activo=True)
            paciente = request.user.perfil_paciente
            
            # Crear turno
            turno = Turno(
                paciente=paciente,
                medico=medico,
                especialidad=especialidad,
                fecha=fecha,
                hora=hora,
                motivo_consulta=motivo_consulta,
                estado='pendiente'
            )
            
            # Validar que no haya sobreposición
            if turno.tiene_sobreposicion():
                messages.error(request, 'Ya existe un turno en ese horario para el médico seleccionado. Por favor, elija otro horario.')
                return redirect('paciente_nuevo_turno_paso1')
            
            turno.save()
            
            # Limpiar sesión
            del request.session['turno_especialidad_id']
            del request.session['turno_fecha']
            del request.session['turno_hora']
            
            messages.success(request, '¡Turno solicitado correctamente! El administrador lo validará pronto.')
            return redirect('paciente_mis_turnos')
            
        except Medico.DoesNotExist:
            messages.error(request, 'Médico no válido.')
            return redirect('paciente_nuevo_turno_paso2')
    
    # Obtener médicos disponibles para ese horario y especialidad
    dia_semana = fecha.weekday()
    
    # Médicos con horario de atención en ese día y hora
    medicos_con_horario = HorarioAtencion.objects.filter(
        dia_semana=dia_semana,
        hora_inicio__lte=hora,
        hora_fin__gt=hora,
        activo=True,
        medico__especialidades=especialidad,
        medico__activo=True
    ).select_related('medico__usuario').distinct()
    
    # Filtrar médicos que NO tienen turno activo en ese horario
    medicos_disponibles = []
    for horario in medicos_con_horario:
        tiene_turno = Turno.objects.filter(
            medico=horario.medico,
            fecha=fecha,
            hora=hora,
            estado__in=['activo', 'en_atencion']
        ).exists()
        
        if not tiene_turno:
            medicos_disponibles.append(horario.medico)
    
    context = {
        'especialidad': especialidad,
        'fecha': fecha,
        'hora': hora,
        'medicos_disponibles': medicos_disponibles,
    }
    return render(request, 'appointments/paciente/nuevo_turno_paso2.html', context)


@login_required
def api_horarios_disponibles_especialidad(request):
    """API para obtener horarios disponibles por especialidad y fecha"""
    especialidad_id = request.GET.get('especialidad_id')
    fecha_str = request.GET.get('fecha')
    
    if not especialidad_id or not fecha_str:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    
    try:
        especialidad = Especialidad.objects.get(id=especialidad_id, activo=True)
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    
    # Validar que sea día laboral
    es_laboral, mensaje = es_dia_laboral(fecha)
    if not es_laboral:
        return JsonResponse({'error': mensaje}, status=400)
    
    dia_semana = fecha.weekday()
    
    # Obtener todos los horarios de médicos de esa especialidad
    horarios_atencion = HorarioAtencion.objects.filter(
        dia_semana=dia_semana,
        activo=True,
        medico__especialidades=especialidad,
        medico__activo=True
    ).select_related('medico')
    
    # Generar slots cada 30 minutos
    slots_disponibles = set()
    
    for horario in horarios_atencion:
        hora_actual = horario.hora_inicio
        while hora_actual < horario.hora_fin:
            # Verificar si hay al menos un médico disponible en este horario
            hay_medico_disponible = False
            
            for h in horarios_atencion:
                if h.hora_inicio <= hora_actual < h.hora_fin:
                    # Verificar que este médico no tenga turno
                    tiene_turno = Turno.objects.filter(
                        medico=h.medico,
                        fecha=fecha,
                        hora=hora_actual,
                        estado__in=['activo', 'en_atencion']
                    ).exists()
                    
                    if not tiene_turno:
                        hay_medico_disponible = True
                        break
            
            if hay_medico_disponible:
                slots_disponibles.add(hora_actual.strftime('%H:%M'))
            
            # Incrementar 30 minutos
            hora_actual = (datetime.combine(fecha, hora_actual) + timedelta(minutes=30)).time()
    
    # Ordenar y devolver
    slots_ordenados = sorted(list(slots_disponibles))
    slots_json = [{'hora': slot} for slot in slots_ordenados]
    
    return JsonResponse(slots_json, safe=False)
