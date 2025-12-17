# Cambios Implementados en MediTurnos

## 1. Médico Opcional en Solicitud de Turnos

### Cambios realizados:
- El campo médico ahora es **opcional** al solicitar un turno
- Implementado **buscador con autocompletado** en lugar de menú desplegable
- Si no se selecciona médico, se muestran horarios de **todos los médicos** de la especialidad elegida
- El sistema es más práctico cuando hay muchos médicos

### Cómo funciona:
1. El paciente selecciona una especialidad (obligatorio)
2. Opcionalmente puede buscar un médico específico escribiendo su nombre
3. Al elegir fecha, se muestran horarios disponibles
4. Si seleccionó médico: solo horarios de ese médico
5. Si NO seleccionó médico: horarios de todos los médicos de la especialidad

---

## 2. Validación de Fecha de Nacimiento

### Cambios realizados:
- El calendario no permite seleccionar fechas futuras (atributo `max`)
- Si se escribe manualmente una fecha inválida, el sistema rechaza el registro
- Mensaje de error claro: *"La fecha de nacimiento no puede ser posterior a la fecha actual"*

---

## 3. Validación de Edad Mínima

### Cambios realizados:
- **Edad mínima requerida: 18 años** (edad legal para turnos autónomos en Argentina)
- Si es menor de 18 años, el sistema rechaza el registro
- Mensaje de error: *"Debe tener al menos 18 años para registrarse y solicitar turnos de forma autónoma. Si es menor de edad, debe asistir con un adulto responsable."*

---

## 4. Sistema Mejorado de Obras Sociales

### Cambios realizados:
- Creado modelo `ObraSocial` en la base de datos
- Campo cambiado de texto libre a **selector con opciones predefinidas**
- Incluye las obras sociales más comunes de Argentina:
  - Obras sociales nacionales (OSEP, PAMI, UPCN, OSECAC, etc.)
  - Prepagas (OSDE, Swiss Medical, Galeno, Medicus, OMINT, etc.)
  - Obras sociales provinciales (IOSPER, APROSS, IPS, etc.)
- Opción "Particular (sin obra social)" disponible
- **Migración segura**: Mantiene el campo antiguo para compatibilidad con datos existentes

### Implementación técnica:
- `obra_social` (CharField): Campo legacy que mantiene los datos antiguos
- `obra_social_obj` (ForeignKey): Nuevo campo que referencia al modelo ObraSocial
- Método `get_obra_social_display()`: Prioriza el nuevo campo sobre el antiguo
- Script de migración automática que intenta emparejar obras sociales existentes

### Obras sociales incluidas (35 opciones):
- **15 obras sociales nacionales** más comunes
- **10 prepagas** principales
- **10 obras sociales provinciales** representativas

---

## 🔧 Instrucciones para Aplicar los Cambios

### 1. Crear las migraciones:
```bash
python manage.py makemigrations
```

### 2. Aplicar las migraciones:
```bash
python manage.py migrate
```

### 3. Ejecutar comandos de datos:
```bash
python manage.py cargar_obras_sociales
python manage.py migrar_obras_sociales
```

El comando `migrar_obras_sociales` intentará emparejar automáticamente las obras sociales en texto con las del catálogo. Si no encuentra coincidencia, los pacientes podrán actualizar su obra social desde su perfil.

### 4. (Opcional) Convertir datos existentes:
Si ya tienes pacientes con obras sociales en texto, necesitarás crear una migración de datos para convertirlos al nuevo formato.

---

## 📋 Ventajas del nuevo sistema

### Turnos:
- ✅ Más rápido: no necesitas elegir médico si no tienes preferencia
- ✅ Más flexible: puedes elegir cualquier horario disponible de la especialidad
- ✅ Más práctico: buscador en lugar de lista desplegable larga

### Registro:
- ✅ Más seguro: no se pueden registrar fechas de nacimiento inválidas
- ✅ Cumple con requisitos legales: edad mínima de 18 años
- ✅ Mensajes de error claros y específicos

### Obras Sociales:
- ✅ Datos estandarizados: todas las obras sociales con mismo formato
- ✅ Fácil de buscar: selector con opciones ordenadas
- ✅ Extensible: se pueden agregar más obras sociales fácilmente
- ✅ Integrado: usa modelo de base de datos en lugar de texto libre

---

## 🔄 Compatibilidad con Render

Todos los cambios son compatibles con el despliegue en Render. El [build.sh](build.sh) ya está configurado para:

1. Ejecutar migraciones automáticamente
2. Cargar el catálogo de obras sociales
3. Migrar obras sociales existentes de texto a modelo

**No requiere acción manual** - simplemente haz push y Render ejecutará todo automáticamente.

---

## 📝 Notas adicionales

### Migración de datos existentes:
El sistema mantiene **compatibilidad con datos antiguos**:
- Campo `obra_social` (texto): Se mantiene con los datos legacy
- Campo `obra_social_obj` (ForeignKey): Nuevo campo para el modelo
- El script de migración intenta emparejar automáticamente por nombre o sigla
- Si no hay coincidencia, el paciente puede actualizar su perfil manualmente

### Para limpiar datos legacy (opcional):
Una vez que todos los pacientes hayan migrado a `obra_social_obj`, puedes:
1. Eliminar el campo `obra_social` del modelo
2. Renombrar `obra_social_obj` a `obra_social`
3. Crear y aplicar una migración

### Agregar más obras sociales:
Simplemente edita el archivo `appointments/management/commands/cargar_obras_sociales.py` y vuelve a ejecutar el comando.
