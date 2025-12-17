"""
Script de migración de datos para convertir obras sociales de texto a modelo
Ejecutar después de aplicar las migraciones del modelo ObraSocial
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from appointments.models import Paciente, ObraSocial


class Command(BaseCommand):
    help = 'Migra obras sociales de campo texto (obra_social) a ForeignKey (obra_social_obj)'
    
    def handle(self, *args, **kwargs):
        # Obtener todos los pacientes que tienen texto pero no FK
        pacientes = Paciente.objects.filter(
            obra_social_obj__isnull=True
        ).exclude(
            Q(obra_social='') | Q(obra_social__isnull=True)
        )
        
        total = pacientes.count()
        migrados = 0
        no_encontrados = []
        
        self.stdout.write(f'Procesando {total} pacientes con obra social en texto...\n')
        
        for paciente in pacientes:
            obra_social_texto = paciente.obra_social.strip()
            
            # Buscar coincidencia en obras sociales
            obra_social_obj = ObraSocial.objects.filter(
                Q(nombre__icontains=obra_social_texto) |
                Q(sigla__iexact=obra_social_texto)
            ).first()
            
            if obra_social_obj:
                paciente.obra_social_obj = obra_social_obj
                paciente.save()
                migrados += 1
                self.stdout.write(f'✓ {paciente.usuario.get_full_name()}: "{obra_social_texto}" → {obra_social_obj}')
            else:
                no_encontrados.append((paciente, obra_social_texto))
                self.stdout.write(f'⚠ {paciente.usuario.get_full_name()}: "{obra_social_texto}" - No se encontró coincidencia')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Proceso completado'))
        self.stdout.write(f'  - Total procesados: {total}')
        self.stdout.write(f'  - Migrados exitosamente: {migrados}')
        self.stdout.write(f'  - Sin coincidencia: {len(no_encontrados)}')
        
        if no_encontrados:
            self.stdout.write(self.style.WARNING(f'\nObras sociales sin coincidencia:'))
            for paciente, texto in no_encontrados:
                self.stdout.write(f'  - "{texto}" (paciente: {paciente.usuario.get_full_name()})')
            self.stdout.write(f'\nEstos pacientes pueden actualizar su obra social desde su perfil.')
