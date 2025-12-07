from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time, date, timedelta

from appointments.models import (
    Usuario, Paciente, Medico, Especialidad, 
    HorarioAtencion, Turno, ConfiguracionSistema
)


class Command(BaseCommand):
    help = 'Carga datos de prueba en la base de datos para desarrollo y testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos antes de cargar los nuevos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('⚠️  Eliminando datos existentes...'))
            Turno.objects.all().delete()
            HorarioAtencion.objects.all().delete()
            Paciente.objects.all().delete()
            Medico.objects.all().delete()
            Especialidad.objects.all().delete()
            Usuario.objects.filter(is_superuser=False).delete()
            ConfiguracionSistema.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Datos eliminados'))

        self.stdout.write(self.style.SUCCESS('🔄 Iniciando carga de datos de prueba...'))
        
        # 1. Crear configuración del sistema
        self.stdout.write('\n📋 Creando configuración del sistema...')
        config, created = ConfiguracionSistema.objects.get_or_create(
            pk=1,
            defaults={
                'nombre_consultorio': 'MediTurnos',
                'direccion': 'Av. Corrientes 1234, CABA',
                'telefono': '011-4567-8900',
                'email': 'info@mediturnos.com',
                'horario_apertura': time(7, 0),
                'horario_cierre': time(16, 0),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('   ✓ Configuración creada'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠ Configuración ya existía'))
        
        # 2. Crear especialidades
        self.stdout.write('\n🏥 Creando especialidades...')
        especialidades_data = [
            {'nombre': 'Cardiología', 'descripcion': 'Atención del corazón y sistema circulatorio', 'duracion_turno': 30},
            {'nombre': 'Pediatría', 'descripcion': 'Atención médica para niños y adolescentes', 'duracion_turno': 30},
            {'nombre': 'Traumatología', 'descripcion': 'Lesiones del sistema musculoesquelético', 'duracion_turno': 30},
            {'nombre': 'Clínica Médica', 'descripcion': 'Medicina general y preventiva', 'duracion_turno': 30},
            {'nombre': 'Dermatología', 'descripcion': 'Enfermedades de la piel', 'duracion_turno': 30},
        ]
        
        especialidades = {}
        for esp_data in especialidades_data:
            esp, created = Especialidad.objects.get_or_create(
                nombre=esp_data['nombre'],
                defaults=esp_data
            )
            especialidades[esp_data['nombre']] = esp
            status = '✓ Creada' if created else '⚠ Ya existía'
            self.stdout.write(f"   {status}: {esp_data['nombre']}")
        
        # 3. Crear usuario administrador
        self.stdout.write('\n👑 Creando usuario administrador...')
        admin, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'appointments',
                'email': 'admin@mediturnos.com',
                'dni': '12345678',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('   ✓ Administrador creado (username: admin, password: admin123)'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠ Administrador ya existía'))
        
        # 4. Crear médicos
        self.stdout.write('\n👨‍⚕️ Creando médicos...')
        medicos_data = [
            {
                'username': 'mgonzalez',
                'password': 'medico123',
                'first_name': 'María',
                'last_name': 'González',
                'email': 'mgonzalez@mediturnos.com',
                'dni': '30123456',
                'telefono': '011-1234-5678',
                'matricula': 'MN12345',
                'especialidades': ['Cardiología', 'Clínica Médica'],
                'biografia': 'Especialista en cardiología con 15 años de experiencia.'
            },
            {
                'username': 'crodriguez',
                'password': 'medico123',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'email': 'crodriguez@mediturnos.com',
                'dni': '28456789',
                'telefono': '011-2345-6789',
                'matricula': 'MN23456',
                'especialidades': ['Pediatría'],
                'biografia': 'Pediatra con especialización en neonatología.'
            },
            {
                'username': 'jmartinez',
                'password': 'medico123',
                'first_name': 'Juan',
                'last_name': 'Martínez',
                'email': 'jmartinez@mediturnos.com',
                'dni': '32789012',
                'telefono': '011-3456-7890',
                'matricula': 'MN34567',
                'especialidades': ['Traumatología'],
                'biografia': 'Traumatólogo especializado en medicina deportiva.'
            },
            {
                'username': 'alopez',
                'password': 'medico123',
                'first_name': 'Ana',
                'last_name': 'López',
                'email': 'alopez@mediturnos.com',
                'dni': '29234567',
                'telefono': '011-4567-8901',
                'matricula': 'MN45678',
                'especialidades': ['Dermatología'],
                'biografia': 'Dermatóloga con enfoque en dermatología estética.'
            },
            {
                'username': 'rfernandez',
                'password': 'medico123',
                'first_name': 'Roberto',
                'last_name': 'Fernández',
                'email': 'rfernandez@mediturnos.com',
                'dni': '31567890',
                'telefono': '011-5678-9012',
                'matricula': 'MN56789',
                'especialidades': ['Clínica Médica', 'Cardiología'],
                'biografia': 'Médico clínico con especialización en medicina preventiva.'
            },
        ]
        
        medicos_creados = []
        for med_data in medicos_data:
            # Crear usuario
            usuario, created = Usuario.objects.get_or_create(
                username=med_data['username'],
                defaults={
                    'first_name': med_data['first_name'],
                    'last_name': med_data['last_name'],
                    'email': med_data['email'],
                    'dni': med_data['dni'],
                    'telefono': med_data['telefono'],
                    'rol': 'medico'
                }
            )
            if created:
                usuario.set_password(med_data['password'])
                usuario.save()
            
            # Crear perfil de médico
            medico, medico_created = Medico.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'matricula': med_data['matricula'],
                    'biografia': med_data['biografia'],
                    'activo': True
                }
            )
            
            # Asignar especialidades
            for esp_nombre in med_data['especialidades']:
                medico.especialidades.add(especialidades[esp_nombre])
            
            medicos_creados.append(medico)
            status = '✓ Creado' if created else '⚠ Ya existía'
            self.stdout.write(f"   {status}: Dr/a. {med_data['first_name']} {med_data['last_name']} - {', '.join(med_data['especialidades'])}")
        
        # 5. Crear horarios de atención para los médicos
        self.stdout.write('\n🕐 Creando horarios de atención...')
        horarios_creados = 0
        for medico in medicos_creados:
            # Lunes a Viernes de 9:00 a 13:00
            for dia in range(5):  # 0=Lunes a 4=Viernes
                _, created = HorarioAtencion.objects.get_or_create(
                    medico=medico,
                    dia_semana=dia,
                    hora_inicio=time(9, 0),
                    hora_fin=time(13, 0),
                    defaults={'activo': True}
                )
                if created:
                    horarios_creados += 1
        self.stdout.write(self.style.SUCCESS(f'   ✓ {horarios_creados} horarios creados'))
        
        # 6. Crear pacientes
        self.stdout.write('\n👨‍👩‍👧‍👦 Creando pacientes de prueba...')
        pacientes_data = [
            {
                'username': 'jperez',
                'password': 'paciente123',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'email': 'jperez@email.com',
                'dni': '35123456',
                'telefono': '011-9876-5432',
                'fecha_nacimiento': date(1990, 5, 15),
                'obra_social': 'OSDE',
                'numero_afiliado': '123456789'
            },
            {
                'username': 'mfernandez',
                'password': 'paciente123',
                'first_name': 'María',
                'last_name': 'Fernández',
                'email': 'mfernandez@email.com',
                'dni': '36234567',
                'telefono': '011-8765-4321',
                'fecha_nacimiento': date(1985, 8, 20),
                'obra_social': 'Swiss Medical',
                'numero_afiliado': '987654321'
            },
            {
                'username': 'lgarcia',
                'password': 'paciente123',
                'first_name': 'Luis',
                'last_name': 'García',
                'email': 'lgarcia@email.com',
                'dni': '37345678',
                'telefono': '011-7654-3210',
                'fecha_nacimiento': date(1995, 3, 10),
                'obra_social': 'Galeno',
                'numero_afiliado': '456789123'
            },
        ]
        
        pacientes_creados = []
        for pac_data in pacientes_data:
            # Crear usuario
            usuario, created = Usuario.objects.get_or_create(
                username=pac_data['username'],
                defaults={
                    'first_name': pac_data['first_name'],
                    'last_name': pac_data['last_name'],
                    'email': pac_data['email'],
                    'dni': pac_data['dni'],
                    'telefono': pac_data['telefono'],
                    'fecha_nacimiento': pac_data['fecha_nacimiento'],
                    'rol': 'paciente'
                }
            )
            if created:
                usuario.set_password(pac_data['password'])
                usuario.save()
            
            # Crear perfil de paciente
            paciente, paciente_created = Paciente.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'obra_social': pac_data['obra_social'],
                    'numero_afiliado': pac_data['numero_afiliado']
                }
            )
            
            pacientes_creados.append(paciente)
            status = '✓ Creado' if created else '⚠ Ya existía'
            self.stdout.write(f"   {status}: {pac_data['first_name']} {pac_data['last_name']}")
        
        # 7. Crear turnos de ejemplo
        self.stdout.write('\n📅 Creando turnos de ejemplo...')
        hoy = date.today()
        manana = hoy + timedelta(days=1)
        pasado_manana = hoy + timedelta(days=2)
        
        turnos_data = [
            {
                'paciente': pacientes_creados[0],
                'medico': medicos_creados[0],
                'especialidad': especialidades['Cardiología'],
                'fecha': manana,
                'hora': time(9, 0),
                'motivo_consulta': 'Control de rutina',
                'estado': 'pendiente'
            },
            {
                'paciente': pacientes_creados[1],
                'medico': medicos_creados[1],
                'especialidad': especialidades['Pediatría'],
                'fecha': manana,
                'hora': time(10, 0),
                'motivo_consulta': 'Control de crecimiento',
                'estado': 'confirmado'
            },
            {
                'paciente': pacientes_creados[2],
                'medico': medicos_creados[2],
                'especialidad': especialidades['Traumatología'],
                'fecha': pasado_manana,
                'hora': time(9, 30),
                'motivo_consulta': 'Dolor en rodilla',
                'estado': 'pendiente'
            },
        ]
        
        turnos_creados = 0
        for turno_data in turnos_data:
            turno, created = Turno.objects.get_or_create(
                paciente=turno_data['paciente'],
                medico=turno_data['medico'],
                fecha=turno_data['fecha'],
                hora=turno_data['hora'],
                defaults={
                    'especialidad': turno_data['especialidad'],
                    'motivo_consulta': turno_data['motivo_consulta'],
                    'estado': turno_data['estado']
                }
            )
            if created:
                turnos_creados += 1
                self.stdout.write(f"   ✓ Turno: {turno_data['paciente'].usuario.get_full_name()} con {turno_data['medico']}")
        
        # Resumen final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ ¡DATOS DE PRUEBA CARGADOS CORRECTAMENTE!'))
        self.stdout.write('='*60)
        self.stdout.write('\n📝 CREDENCIALES DE ACCESO:')
        self.stdout.write('\n🔐 ADMINISTRADOR:')
        self.stdout.write('   Username: admin')
        self.stdout.write('   Password: admin123')
        self.stdout.write('\n👨‍⚕️ MÉDICOS (todos con password: medico123):')
        self.stdout.write('   - mgonzalez (Dra. María González - Cardiología)')
        self.stdout.write('   - crodriguez (Dr. Carlos Rodríguez - Pediatría)')
        self.stdout.write('   - jmartinez (Dr. Juan Martínez - Traumatología)')
        self.stdout.write('   - alopez (Dra. Ana López - Dermatología)')
        self.stdout.write('   - rfernandez (Dr. Roberto Fernández - Clínica Médica)')
        self.stdout.write('\n👤 PACIENTES (todos con password: paciente123):')
        self.stdout.write('   - jperez (Juan Pérez)')
        self.stdout.write('   - mfernandez (María Fernández)')
        self.stdout.write('   - lgarcia (Luis García)')
        self.stdout.write('\n' + '='*60)
