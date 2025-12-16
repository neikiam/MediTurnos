"""
Utilidades para el manejo de fechas y feriados
"""
from datetime import date
from typing import List, Tuple


def obtener_feriados_argentina(anio: int = None) -> List[date]:
    """
    Retorna una lista de feriados nacionales de Argentina para un año dado.
    Si no se especifica año, usa el año actual.
    
    Incluye feriados fijos y algunos móviles importantes.
    """
    if anio is None:
        anio = date.today().year
    
    feriados = [
        # Feriados fijos
        date(anio, 1, 1),   # Año Nuevo
        date(anio, 2, 24),  # Día de la Bandera (si cae lunes)
        date(anio, 3, 24),  # Día Nacional de la Memoria por la Verdad y la Justicia
        date(anio, 4, 2),   # Día del Veterano y de los Caídos en la Guerra de Malvinas
        date(anio, 5, 1),   # Día del Trabajador
        date(anio, 5, 25),  # Día de la Revolución de Mayo
        date(anio, 6, 20),  # Día de la Bandera Nacional
        date(anio, 7, 9),   # Día de la Independencia
        date(anio, 8, 17),  # Paso a la Inmortalidad del General José de San Martín (si cae lunes)
        date(anio, 10, 12), # Día del Respeto a la Diversidad Cultural (si cae lunes)
        date(anio, 11, 20), # Día de la Soberanía Nacional (si cae lunes)
        date(anio, 12, 8),  # Inmaculada Concepción de María
        date(anio, 12, 25), # Navidad
    ]
    
    # Feriados móviles específicos por año (Semana Santa principalmente)
    feriados_moviles = obtener_feriados_moviles(anio)
    feriados.extend(feriados_moviles)
    
    return sorted(set(feriados))  # Eliminar duplicados y ordenar


def obtener_feriados_moviles(anio: int) -> List[date]:
    """
    Retorna feriados móviles para un año específico.
    Nota: Semana Santa cambia cada año, aquí hay algunas fechas aproximadas.
    Para precisión completa, se recomienda usar una biblioteca de fechas litúrgicas.
    """
    feriados_moviles_por_anio = {
        2024: [
            date(2024, 3, 28),  # Jueves Santo
            date(2024, 3, 29),  # Viernes Santo
            date(2024, 2, 12),  # Carnaval (lunes)
            date(2024, 2, 13),  # Carnaval (martes)
        ],
        2025: [
            date(2025, 4, 17),  # Jueves Santo
            date(2025, 4, 18),  # Viernes Santo
            date(2025, 3, 3),   # Carnaval (lunes)
            date(2025, 3, 4),   # Carnaval (martes)
        ],
        2026: [
            date(2026, 4, 2),   # Jueves Santo
            date(2026, 4, 3),   # Viernes Santo
            date(2026, 2, 16),  # Carnaval (lunes)
            date(2026, 2, 17),  # Carnaval (martes)
        ],
        2027: [
            date(2027, 3, 25),  # Jueves Santo
            date(2027, 3, 26),  # Viernes Santo
            date(2027, 2, 8),   # Carnaval (lunes)
            date(2027, 2, 9),   # Carnaval (martes)
        ],
    }
    
    return feriados_moviles_por_anio.get(anio, [])


def es_feriado(fecha: date) -> Tuple[bool, str]:
    """
    Verifica si una fecha es feriado en Argentina.
    
    Returns:
        Tuple[bool, str]: (es_feriado, nombre_del_feriado)
    """
    nombres_feriados = {
        (1, 1): "Año Nuevo",
        (2, 24): "Día de la Bandera",
        (3, 24): "Día Nacional de la Memoria por la Verdad y la Justicia",
        (4, 2): "Día del Veterano y de los Caídos en la Guerra de Malvinas",
        (5, 1): "Día del Trabajador",
        (5, 25): "Día de la Revolución de Mayo",
        (6, 20): "Día de la Bandera Nacional",
        (7, 9): "Día de la Independencia",
        (8, 17): "Paso a la Inmortalidad del General José de San Martín",
        (10, 12): "Día del Respeto a la Diversidad Cultural",
        (11, 20): "Día de la Soberanía Nacional",
        (12, 8): "Inmaculada Concepción de María",
        (12, 25): "Navidad",
    }
    
    # Verificar feriados fijos
    clave = (fecha.month, fecha.day)
    if clave in nombres_feriados:
        return True, nombres_feriados[clave]
    
    # Verificar feriados móviles
    feriados_moviles = obtener_feriados_moviles(fecha.year)
    if fecha in feriados_moviles:
        # Determinar qué feriado móvil es
        mes_dia = (fecha.month, fecha.day)
        if fecha.month == 2 or fecha.month == 3:
            if fecha.weekday() == 0:  # Lunes
                return True, "Carnaval"
            elif fecha.weekday() == 1:  # Martes
                return True, "Carnaval"
        if fecha.month in [3, 4]:
            # Semana Santa
            dia_semana = fecha.weekday()
            if dia_semana == 3:  # Jueves
                return True, "Jueves Santo"
            elif dia_semana == 4:  # Viernes
                return True, "Viernes Santo"
    
    return False, ""


def es_fin_de_semana(fecha: date) -> bool:
    """
    Verifica si una fecha cae en fin de semana (sábado o domingo).
    """
    return fecha.weekday() in [5, 6]  # 5=sábado, 6=domingo


def es_dia_laboral(fecha: date) -> Tuple[bool, str]:
    """
    Verifica si una fecha es día laboral (no es fin de semana ni feriado).
    
    Returns:
        Tuple[bool, str]: (es_laboral, mensaje_error)
    """
    if es_fin_de_semana(fecha):
        return False, "No se pueden solicitar turnos los fines de semana"
    
    es_fer, nombre_feriado = es_feriado(fecha)
    if es_fer:
        return False, f"No se pueden solicitar turnos en feriados: {nombre_feriado}"
    
    return True, ""
