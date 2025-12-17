#!/usr/bin/env bash
set -o errexit

echo "Limpiando caché..."
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "Instalando dependencias..."
pip install --upgrade pip --no-cache-dir
pip install -r requirements.txt --no-cache-dir

echo "Ejecutando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput --fake-initial

echo "Colectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "Creando superusuario si no existe..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import os
import sys

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

# Solo crear superusuario si todas las variables de entorno están definidas
if username and email and password:
    try:
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            print(f'Superuser {username} already exists')
        else:
            # Buscar un DNI único
            dni = '00000000'
            counter = 0
            while User.objects.filter(dni=dni).exists():
                counter += 1
                dni = f'{counter:08d}'
            
            # Crear superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                dni=dni,
                rol='admin'
            )
            print(f'Superuser {username} created successfully with DNI {dni}')
    except Exception as e:
        print(f'Error creating superuser: {e}')
        # No fallar el build si el superusuario no se puede crear
        pass
else:
    print('Skipping superuser creation: environment variables not set')
    print('Required: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD')
EOF

echo "Cargando obras sociales..."
python manage.py cargar_obras_sociales

echo "Migrando obras sociales existentes..."
python manage.py migrar_obras_sociales

echo "Build completado exitosamente"