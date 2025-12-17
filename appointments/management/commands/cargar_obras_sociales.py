"""
Comando para cargar obras sociales argentinas predefinidas
"""
from django.core.management.base import BaseCommand
from appointments.models import ObraSocial


class Command(BaseCommand):
    help = 'Carga obras sociales argentinas predefinidas'
    
    def handle(self, *args, **kwargs):
        obras_sociales = [
            # Obras Sociales Nacionales más comunes
            {'nombre': 'Obra Social de Empleados Públicos', 'sigla': 'OSEP', 'orden': 1},
            {'nombre': 'Instituto Nacional de Servicios Sociales para Jubilados y Pensionados', 'sigla': 'PAMI', 'orden': 2},
            {'nombre': 'Obra Social del Personal de la Construcción', 'sigla': 'OSPOCE', 'orden': 3},
            {'nombre': 'Obra Social de la Unión del Personal Civil de la Nación', 'sigla': 'UPCN', 'orden': 4},
            {'nombre': 'Obra Social del Personal de Edificios de Renta y Horizontal', 'sigla': 'OSPERH', 'orden': 5},
            {'nombre': 'Obra Social del Personal de Comercio', 'sigla': 'OSECAC', 'orden': 6},
            {'nombre': 'Obra Social de la Unión Obrera Metalúrgica', 'sigla': 'UOM', 'orden': 7},
            {'nombre': 'Obra Social del Sindicato Mecánicos y Afines del Transporte Automotor', 'sigla': 'OSMATA', 'orden': 8},
            {'nombre': 'Obra Social del Personal de la Sanidad Argentina', 'sigla': 'OSPSIP', 'orden': 9},
            {'nombre': 'Obra Social de Luz y Fuerza', 'sigla': 'OСЛYF', 'orden': 10},
            {'nombre': 'Obra Social para la Actividad Docente', 'sigla': 'OSPLAD', 'orden': 11},
            {'nombre': 'Obra Social del Personal de la Industria del Vestido', 'sigla': 'OSPIV', 'orden': 12},
            {'nombre': 'Obra Social del Personal de la Alimentación', 'sigla': 'OSPA', 'orden': 13},
            {'nombre': 'Obra Social de los Trabajadores de la Industria del Gas', 'sigla': 'OSTIG', 'orden': 14},
            {'nombre': 'Obra Social del Personal de la Actividad del Turf', 'sigla': 'OSPAT', 'orden': 15},
            
            # Prepagas más comunes
            {'nombre': 'Swiss Medical', 'sigla': 'SWISS', 'orden': 20},
            {'nombre': 'OSDE', 'sigla': 'OSDE', 'orden': 21},
            {'nombre': 'Galeno', 'sigla': 'GALENO', 'orden': 22},
            {'nombre': 'Medicus', 'sigla': 'MEDICUS', 'orden': 23},
            {'nombre': 'OMINT', 'sigla': 'OMINT', 'orden': 24},
            {'nombre': 'Accord Salud', 'sigla': 'ACCORD', 'orden': 25},
            {'nombre': 'Sancor Salud', 'sigla': 'SANCOR', 'orden': 26},
            {'nombre': 'Federada Salud', 'sigla': 'FEDERADA', 'orden': 27},
            {'nombre': 'Prevención Salud', 'sigla': 'PREVENCION', 'orden': 28},
            {'nombre': 'Avalian', 'sigla': 'AVALIAN', 'orden': 29},
            
            # Obras Sociales Provinciales (ejemplos principales)
            {'nombre': 'Instituto de Obra Social de la Provincia de Entre Ríos', 'sigla': 'IOSPER', 'orden': 30},
            {'nombre': 'Obra Social de la Provincia de Córdoba', 'sigla': 'APROSS', 'orden': 31},
            {'nombre': 'Instituto Provincial de Salud de Salta', 'sigla': 'IPS SALTA', 'orden': 32},
            {'nombre': 'Instituto de Previsión Social de Misiones', 'sigla': 'IPS MISIONES', 'orden': 33},
            {'nombre': 'Obra Social del Personal de la Universidad Nacional de Córdoba', 'sigla': 'APUNCO', 'orden': 34},
        ]
        
        creadas = 0
        existentes = 0
        
        for os_data in obras_sociales:
            obra_social, created = ObraSocial.objects.get_or_create(
                nombre=os_data['nombre'],
                defaults={
                    'sigla': os_data['sigla'],
                    'orden': os_data['orden'],
                    'activo': True
                }
            )
            
            if created:
                creadas += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creada: {obra_social}'))
            else:
                existentes += 1
                self.stdout.write(f'  Ya existe: {obra_social}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Proceso completado'))
        self.stdout.write(f'  - Obras sociales creadas: {creadas}')
        self.stdout.write(f'  - Obras sociales existentes: {existentes}')
        self.stdout.write(f'  - Total: {creadas + existentes}')
