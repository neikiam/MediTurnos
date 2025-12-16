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
python manage.py migrate --noinput

echo "Colectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "Creando superusuario si no existe..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@mediturnos.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        dni='00000000',
        rol='admin'
    )
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
EOF

echo "Build completado exitosamente"