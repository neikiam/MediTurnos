# Guía de Despliegue en Render

## Variables de Entorno Requeridas

Configura las siguientes variables de entorno en Render:

### Obligatorias:
```
DJANGO_SECRET_KEY=tu-clave-secreta-generada
DEBUG=False
ALLOWED_HOSTS=tu-app.onrender.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Para Superusuario (opcional, se genera automáticamente):
```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@mediturnos.com
DJANGO_SUPERUSER_PASSWORD=tu-contraseña-segura
```

## Pasos para Desplegar

1. **Conecta tu repositorio de GitHub a Render**

2. **Configura el servicio web:**
   - Build Command: `./build.sh`
   - Start Command: `gunicorn config.wsgi:application`
   - Environment: Python 3

3. **Crea una base de datos PostgreSQL en Render**
   - Nombre: `mediturnos-db`
   - Copia el Internal Database URL

4. **Configura las variables de entorno:**
   - Pega el DATABASE_URL de tu base de datos
   - Genera DJANGO_SECRET_KEY (puedes usar: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - Configura ALLOWED_HOSTS con tu dominio de Render (ej: `tu-app.onrender.com`)

5. **Despliega:**
   - Render ejecutará automáticamente `build.sh`
   - Se instalarán dependencias
   - Se ejecutarán migraciones
   - Se crearán archivos estáticos
   - Se creará el superusuario automáticamente

## Solución de Problemas Comunes

### Error 500 - Internal Server Error

**Causa:** Variables de entorno faltantes o configuración incorrecta

**Solución:**
- Verifica que DATABASE_URL esté configurada correctamente
- Asegúrate de que ALLOWED_HOSTS incluya tu dominio de Render
- Revisa los logs en Render Dashboard

### Error al crear superusuario

**Causa:** DNI requerido en el modelo Usuario

**Solución:**
- El build.sh crea automáticamente el superusuario con DNI '00000000'
- Puedes cambiar el DNI después desde el admin de Django

### Archivos estáticos no cargan

**Causa:** collectstatic no se ejecutó o STATIC_ROOT mal configurado

**Solución:**
- El build.sh ejecuta automáticamente `collectstatic`
- Verifica que WhiteNoise esté en MIDDLEWARE en settings.py

### Error de CSRF

**Causa:** CSRF_TRUSTED_ORIGINS no incluye tu dominio

**Solución:**
- Ya está configurado para *.onrender.com
- Si usas dominio personalizado, agrégalo a ALLOWED_HOSTS

## Verificación Post-Despliegue

1. Visita tu sitio: `https://tu-app.onrender.com`
2. Prueba el login con las credenciales del superusuario
3. Verifica que los archivos estáticos (CSS/JS) cargan correctamente
4. Prueba crear un turno como paciente

## Actualizaciones

Para actualizar la aplicación:
1. Haz push a tu repositorio de GitHub
2. Render detectará automáticamente los cambios
3. Ejecutará el build y desplegará la nueva versión
