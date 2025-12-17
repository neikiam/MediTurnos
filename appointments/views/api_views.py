"""
API endpoints para AJAX
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta

from ..models import Medico, HorarioAtencion, Turno
from ..utils import es_dia_laboral


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
    """Obtener horarios disponibles para especialidad o médico en una fecha (AJAX)"""
    medico_id = request.GET.get('medico_id')
    especialidad_id = request.GET.get('especialidad_id')
    fecha_str = request.GET.get('fecha')
    
    if not fecha_str or (not medico_id and not especialidad_id):
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)
    
    # Validar que sea día laboral (no fin de semana ni feriado)
    es_laboral, mensaje = es_dia_laboral(fecha)
    if not es_laboral:
        return JsonResponse({'error': mensaje}, status=400)
    
    # Obtener día de la semana (0=Lunes, 6=Domingo)
    dia_semana = fecha.weekday()
    
    # Si hay médico específico
    if medico_id:
        try:
            medico = Medico.objects.get(id=medico_id)
            medicos = [medico]
        except:
            return JsonResponse({'error': 'Médico no encontrado'}, status=400)
    # Si solo hay especialidad, buscar todos los médicos
    elif especialidad_id:
        medicos = Medico.objects.filter(
            especialidades__id=especialidad_id,
            activo=True
        )
    else:
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)
    
    # Generar slots disponibles
    slots_disponibles = []
    
    for medico in medicos:
        # Obtener horarios de atención del médico para ese día
        horarios_atencion = HorarioAtencion.objects.filter(
            medico=medico,
            dia_semana=dia_semana,
            activo=True
        )
        
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
                        'medico': str(medico),
                        'medico_id': medico.id,
                        'disponible': True
                    })
                
                # Incrementar 30 minutos
                hora_actual = (datetime.combine(fecha, hora_actual) + timedelta(minutes=30)).time()
    
    # Ordenar por hora
    slots_disponibles.sort(key=lambda x: x['hora'])
    
    return JsonResponse(slots_disponibles, safe=False)
