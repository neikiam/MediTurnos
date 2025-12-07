"""
API endpoints para AJAX
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta

from ..models import Medico, HorarioAtencion, Turno


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
