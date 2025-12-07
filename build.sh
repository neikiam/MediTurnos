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

echo "Build completado exitosamente"
python manage.py createsuperuser --noinput --username "${DJANGO_SUPERUSER_USERNAME:-Neikiam}" --email "${DJANGO_SUPERUSER_EMAIL:-neikiam@500gmail.com}" 2>/dev/null || echo "Superuser already exists or creation skipped"