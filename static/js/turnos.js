/**
 * Funciones específicas para el módulo de turnos
 */

// Confirmar eliminación de turno
async function confirmarEliminarTurno(turnoId, pacienteNombre, fecha, hora) {
    const confirmado = await ConfirmModal.show({
        title: 'Eliminar Turno',
        message: `¿Está seguro de eliminar el turno de <strong>${pacienteNombre}</strong> para el día <strong>${fecha}</strong> a las <strong>${hora}</strong>?<br><br>Esta acción no se puede deshacer.`,
        confirmText: 'Eliminar Turno',
        confirmClass: 'btn-danger',
        icon: 'bi-calendar-x'
    });
    
    if (confirmado) {
        LoadingSpinner.show('Eliminando turno...');
        // El formulario se submitirá automáticamente
        return true;
    }
    return false;
}

// Confirmar cancelación de turno
async function confirmarCancelarTurno(turnoId) {
    const confirmado = await ConfirmModal.show({
        title: 'Cancelar Turno',
        message: '¿Está seguro de cancelar este turno? El paciente será notificado.',
        confirmText: 'Cancelar Turno',
        confirmClass: 'btn-warning',
        icon: 'bi-x-circle'
    });
    
    if (confirmado) {
        LoadingSpinner.show('Cancelando turno...');
        return true;
    }
    return false;
}

// Confirmar atención de turno
async function confirmarAtenderTurno(pacienteNombre) {
    const confirmado = await ConfirmModal.show({
        title: 'Atender Turno',
        message: `¿Comenzar atención del paciente <strong>${pacienteNombre}</strong>?`,
        confirmText: 'Iniciar Atención',
        confirmClass: 'btn-success',
        icon: 'bi-clipboard-check'
    });
    
    return confirmado;
}

// Filtrar turnos por estado
function filtrarTurnosPorEstado(estadoId) {
    const tabla = document.getElementById('tablaTurnos');
    if (!tabla) return;
    
    const filas = tabla.querySelectorAll('tbody tr:not(.no-results-row)');
    let visibleCount = 0;
    
    filas.forEach(fila => {
        if (!estadoId) {
            fila.style.display = '';
            visibleCount++;
        } else {
            const badge = fila.querySelector('.badge-estado');
            if (badge && badge.classList.contains(`badge-${estadoId}`)) {
                fila.style.display = '';
                visibleCount++;
            } else {
                fila.style.display = 'none';
            }
        }
    });
    
    updateNoResultsMessage(tabla.querySelector('tbody'), visibleCount === 0);
}

// Filtrar por fecha
function filtrarTurnosPorFecha(fechaDesde, fechaHasta) {
    const tabla = document.getElementById('tablaTurnos');
    if (!tabla) return;
    
    const filas = tabla.querySelectorAll('tbody tr:not(.no-results-row)');
    let visibleCount = 0;
    
    const desde = fechaDesde ? new Date(fechaDesde) : null;
    const hasta = fechaHasta ? new Date(fechaHasta) : null;
    
    filas.forEach(fila => {
        const fechaCell = fila.querySelector('[data-fecha]');
        if (!fechaCell) return;
        
        const fechaTurno = new Date(fechaCell.getAttribute('data-fecha'));
        
        let mostrar = true;
        if (desde && fechaTurno < desde) mostrar = false;
        if (hasta && fechaTurno > hasta) mostrar = false;
        
        fila.style.display = mostrar ? '' : 'none';
        if (mostrar) visibleCount++;
    });
    
    updateNoResultsMessage(tabla.querySelector('tbody'), visibleCount === 0);
}
