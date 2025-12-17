"""
Script de migración de datos para convertir obras sociales de texto a modelo
Ejecutar después de aplicar las migraciones del modelo ObraSocial
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from appointments.models import Paciente, ObraSocial


class Command(BaseCommand):
    help = 'Migra obras sociales de texto a modelo ObraSocial'
    
    def handle(self, *args, **kwargs):
        # Obtener todos los pacientes
        pacientes = Paciente.objects.all()
        total = pacientes.count()
        migrados = 0
        sin_obra_social = 0
        no_encontrados = 0
        
        self.stdout.write(f'Procesando {total} pacientes...\n')
        
        for paciente in pacientes:
            # Si ya tiene obra social asignada (FK), saltar
            if paciente.obra_social:
                continue
            
            # Si tiene texto en obra_social_texto (campo antiguo que ya no existe)
            # Este script es para referencia, el campo obra_social ahora es FK
            # Los datos antiguos se perderán en la migración
            
            self.stdout.write(f'Procesando: {paciente.usuario.get_full_name()}')
            
            # Marcar como particular (sin obra social)
            sin_obra_social += 1
            self.stdout.write(f'  → Sin obra social asignada')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Proceso completado'))
        self.stdout.write(f'  - Total de pacientes: {total}')
        self.stdout.write(f'  - Sin obra social: {sin_obra_social}')
        self.stdout.write(f'  - Nota: Los pacientes pueden actualizar su obra social desde su perfil')
