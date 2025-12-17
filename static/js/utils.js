/**
 * Utilidades JavaScript para MediTurnos
 * Modales, Toasts, Confirmaciones, Validaciones
 */

// ============================================
// SISTEMA DE TOASTS (Notificaciones)
// ============================================
const Toast = {
    container: null,
    
    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },
    
    show(message, type = 'info', duration = 5000) {
        this.init();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        }[type] || 'bi-info-circle-fill';
        
        toast.innerHTML = `
            <i class="bi ${icon}"></i>
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;
        
        this.container.appendChild(toast);
        
        // Animación de entrada
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Auto-cerrar
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        return toast;
    },
    
    success(message, duration) {
        return this.show(message, 'success', duration);
    },
    
    error(message, duration) {
        return this.show(message, 'error', duration);
    },
    
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },
    
    info(message, duration) {
        return this.show(message, 'info', duration);
    }
};

// ============================================
// MODALES DE CONFIRMACIÓN
// ============================================
const ConfirmModal = {
    modal: null,
    
    init() {
        if (!this.modal) {
            this.modal = document.createElement('div');
            this.modal.className = 'modal-overlay';
            this.modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"></h5>
                            <button class="modal-close" onclick="ConfirmModal.close()">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                        <div class="modal-body"></div>
                        <div class="modal-footer">
                            <button class="btn btn-secondary" onclick="ConfirmModal.close()">
                                Cancelar
                            </button>
                            <button class="btn btn-danger modal-confirm-btn">
                                Confirmar
                            </button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(this.modal);
        }
    },
    
    show(options = {}) {
        return new Promise((resolve) => {
            this.init();
            
            const {
                title = 'Confirmar Acción',
                message = '¿Está seguro de realizar esta acción?',
                confirmText = 'Confirmar',
                confirmClass = 'btn-danger',
                icon = 'bi-exclamation-triangle'
            } = options;
            
            this.modal.querySelector('.modal-title').innerHTML = `
                <i class="bi ${icon}"></i> ${title}
            `;
            this.modal.querySelector('.modal-body').innerHTML = `<p>${message}</p>`;
            
            const confirmBtn = this.modal.querySelector('.modal-confirm-btn');
            confirmBtn.textContent = confirmText;
            confirmBtn.className = `btn ${confirmClass} modal-confirm-btn`;
            
            // Limpiar eventos anteriores
            const newConfirmBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
            
            newConfirmBtn.onclick = () => {
                this.close();
                resolve(true);
            };
            
            this.modal.style.display = 'flex';
            setTimeout(() => this.modal.classList.add('show'), 10);
            
            // Cerrar con ESC
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    this.close();
                    resolve(false);
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);
        });
    },
    
    close() {
        if (this.modal) {
            this.modal.classList.remove('show');
            setTimeout(() => this.modal.style.display = 'none', 300);
        }
    },
    
    async confirmDelete(itemName, itemType = 'elemento') {
        return await this.show({
            title: 'Confirmar Eliminación',
            message: `¿Está seguro de eliminar ${itemType} <strong>"${itemName}"</strong>? Esta acción no se puede deshacer.`,
            confirmText: 'Eliminar',
            confirmClass: 'btn-danger',
            icon: 'bi-trash'
        });
    }
};

// ============================================
// INDICADOR DE CARGA
// ============================================
const LoadingSpinner = {
    overlay: null,
    
    init() {
        if (!this.overlay) {
            this.overlay = document.createElement('div');
            this.overlay.className = 'loading-overlay';
            this.overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p class="loading-text">Cargando...</p>
                </div>
            `;
            document.body.appendChild(this.overlay);
        }
    },
    
    show(text = 'Cargando...') {
        this.init();
        this.overlay.querySelector('.loading-text').textContent = text;
        this.overlay.style.display = 'flex';
        setTimeout(() => this.overlay.classList.add('show'), 10);
    },
    
    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('show');
            setTimeout(() => this.overlay.style.display = 'none', 300);
        }
    }
};

// ============================================
// BÚSQUEDA EN TIEMPO REAL
// ============================================
function setupTableSearch(inputId, tableId, columnIndexes = null) {
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;
    
    const tbody = table.querySelector('tbody');
    const rows = tbody ? Array.from(tbody.querySelectorAll('tr')) : [];
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        
        rows.forEach(row => {
            if (!searchTerm) {
                row.style.display = '';
                return;
            }
            
            const cells = Array.from(row.querySelectorAll('td'));
            const searchCells = columnIndexes 
                ? cells.filter((_, i) => columnIndexes.includes(i))
                : cells;
            
            const text = searchCells
                .map(cell => cell.textContent.toLowerCase())
                .join(' ');
            
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
        
        // Mostrar mensaje si no hay resultados
        const visibleRows = rows.filter(row => row.style.display !== 'none');
        updateNoResultsMessage(tbody, visibleRows.length === 0);
    });
}

function updateNoResultsMessage(tbody, show) {
    let noResultsRow = tbody.querySelector('.no-results-row');
    
    if (show && !noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = `
            <td colspan="100" class="text-center py-4">
                <i class="bi bi-search" style="font-size: 2rem; color: var(--medical-gray);"></i>
                <p class="text-muted mt-2 mb-0">No se encontraron resultados</p>
            </td>
        `;
        tbody.appendChild(noResultsRow);
    } else if (!show && noResultsRow) {
        noResultsRow.remove();
    }
}

// ============================================
// FILTROS DE TABLA
// ============================================
function setupTableFilters(filters) {
    filters.forEach(filter => {
        const { selectId, tableId, columnIndex } = filter;
        const select = document.getElementById(selectId);
        const table = document.getElementById(tableId);
        
        if (!select || !table) return;
        
        const tbody = table.querySelector('tbody');
        const rows = tbody ? Array.from(tbody.querySelectorAll('tr')) : [];
        
        select.addEventListener('change', function() {
            const filterValue = this.value.toLowerCase();
            
            rows.forEach(row => {
                if (!filterValue) {
                    row.style.display = '';
                    return;
                }
                
                const cell = row.querySelectorAll('td')[columnIndex];
                if (!cell) return;
                
                const cellText = cell.textContent.toLowerCase();
                row.style.display = cellText.includes(filterValue) ? '' : 'none';
            });
        });
    });
}

// ============================================
// VALIDACIÓN DE FORMULARIOS
// ============================================
const FormValidator = {
    rules: {
        required: (value) => value.trim() !== '',
        email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        minLength: (value, min) => value.length >= min,
        maxLength: (value, max) => value.length <= max,
        numeric: (value) => /^\d+$/.test(value),
        alphanumeric: (value) => /^[a-zA-Z0-9]+$/.test(value),
        dni: (value) => /^\d{7,8}$/.test(value),
        phone: (value) => /^\d{10,15}$/.test(value),
    },
    
    messages: {
        required: 'Este campo es obligatorio',
        email: 'Ingrese un email válido',
        minLength: 'Mínimo {min} caracteres',
        maxLength: 'Máximo {max} caracteres',
        numeric: 'Solo números permitidos',
        alphanumeric: 'Solo letras y números',
        dni: 'DNI inválido (7-8 dígitos)',
        phone: 'Teléfono inválido (10-15 dígitos)',
    },
    
    validate(input, rules) {
        const value = input.value;
        const errors = [];
        
        for (const [rule, param] of Object.entries(rules)) {
            const validator = this.rules[rule];
            if (!validator) continue;
            
            const isValid = param === true 
                ? validator(value)
                : validator(value, param);
            
            if (!isValid) {
                let message = this.messages[rule];
                if (typeof param === 'number') {
                    message = message.replace(`{${rule}}`, param);
                }
                errors.push(message);
            }
        }
        
        return errors;
    },
    
    showError(input, errors) {
        this.clearError(input);
        
        if (errors.length > 0) {
            input.classList.add('is-invalid');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = errors[0];
            input.parentNode.appendChild(errorDiv);
            
            return false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            return true;
        }
    },
    
    clearError(input) {
        input.classList.remove('is-invalid', 'is-valid');
        const error = input.parentNode.querySelector('.invalid-feedback');
        if (error) error.remove();
    },
    
    setupRealTimeValidation(formId, fieldRules) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        Object.entries(fieldRules).forEach(([fieldId, rules]) => {
            const input = document.getElementById(fieldId);
            if (!input) return;
            
            input.addEventListener('blur', () => {
                const errors = this.validate(input, rules);
                this.showError(input, errors);
            });
            
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    const errors = this.validate(input, rules);
                    this.showError(input, errors);
                }
            });
        });
        
        form.addEventListener('submit', (e) => {
            let isValid = true;
            
            Object.entries(fieldRules).forEach(([fieldId, rules]) => {
                const input = document.getElementById(fieldId);
                if (!input) return;
                
                const errors = this.validate(input, rules);
                if (!this.showError(input, errors)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                Toast.error('Por favor corrija los errores en el formulario');
            }
        });
    }
};

// ============================================
// TOOLTIPS
// ============================================
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const text = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-popup';
            tooltip.textContent = text;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
            
            setTimeout(() => tooltip.classList.add('show'), 10);
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.classList.remove('show');
                setTimeout(() => this._tooltip.remove(), 200);
                this._tooltip = null;
            }
        });
    });
}

// ============================================
// INICIALIZACIÓN AL CARGAR LA PÁGINA
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    initTooltips();
    
    // Convertir mensajes de Django en toasts
    const djangoMessages = document.querySelectorAll('.alert');
    djangoMessages.forEach(alert => {
        const type = alert.classList.contains('alert-success') ? 'success'
                   : alert.classList.contains('alert-danger') ? 'error'
                   : alert.classList.contains('alert-warning') ? 'warning'
                   : 'info';
        
        Toast.show(alert.textContent.trim(), type);
        alert.remove();
    });
});
