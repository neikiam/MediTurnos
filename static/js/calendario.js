/**
 * Sistema de Calendario para Gestión de Turnos
 */

class CalendarioTurnos {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Contenedor ${containerId} no encontrado`);
            return;
        }
        
        this.options = {
            mesActual: options.mesActual || new Date().getMonth(),
            añoActual: options.añoActual || new Date().getFullYear(),
            onDayClick: options.onDayClick || null,
            turnosPorDia: options.turnosPorDia || {},
            diasDisponibles: options.diasDisponibles || []
        };
        
        this.meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ];
        
        this.diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
        
        this.render();
    }
    
    render() {
        const header = this.createHeader();
        const calendar = this.createCalendar();
        
        this.container.innerHTML = '';
        this.container.appendChild(header);
        this.container.appendChild(calendar);
    }
    
    createHeader() {
        const header = document.createElement('div');
        header.className = 'calendario-header';
        
        const mesAño = document.createElement('h3');
        mesAño.textContent = `${this.meses[this.options.mesActual]} ${this.options.añoActual}`;
        
        const navegacion = document.createElement('div');
        navegacion.className = 'calendario-nav';
        
        const btnAnterior = document.createElement('button');
        btnAnterior.innerHTML = '<i class="bi bi-chevron-left"></i>';
        btnAnterior.className = 'btn btn-sm btn-outline-primary';
        btnAnterior.onclick = () => this.mesAnterior();
        
        const btnSiguiente = document.createElement('button');
        btnSiguiente.innerHTML = '<i class="bi bi-chevron-right"></i>';
        btnSiguiente.className = 'btn btn-sm btn-outline-primary';
        btnSiguiente.onclick = () => this.mesSiguiente();
        
        const btnHoy = document.createElement('button');
        btnHoy.textContent = 'Hoy';
        btnHoy.className = 'btn btn-sm btn-primary mx-2';
        btnHoy.onclick = () => this.irHoy();
        
        navegacion.appendChild(btnAnterior);
        navegacion.appendChild(btnHoy);
        navegacion.appendChild(btnSiguiente);
        
        header.appendChild(mesAño);
        header.appendChild(navegacion);
        
        return header;
    }
    
    createCalendar() {
        const calendar = document.createElement('div');
        calendar.className = 'calendario-grid';
        
        // Encabezados de días
        this.diasSemana.forEach(dia => {
            const header = document.createElement('div');
            header.className = 'calendario-dia-header';
            header.textContent = dia;
            calendar.appendChild(header);
        });
        
        // Días del mes
        const primerDia = new Date(this.options.añoActual, this.options.mesActual, 1).getDay();
        const diasEnMes = new Date(this.options.añoActual, this.options.mesActual + 1, 0).getDate();
        
        // Espacios vacíos antes del primer día
        for (let i = 0; i < primerDia; i++) {
            const empty = document.createElement('div');
            empty.className = 'calendario-dia empty';
            calendar.appendChild(empty);
        }
        
        // Días del mes
        const hoy = new Date();
        const esHoy = (dia) => {
            return dia === hoy.getDate() && 
                   this.options.mesActual === hoy.getMonth() && 
                   this.options.añoActual === hoy.getFullYear();
        };
        
        for (let dia = 1; dia <= diasEnMes; dia++) {
            const diaElement = document.createElement('div');
            diaElement.className = 'calendario-dia';
            
            if (esHoy(dia)) {
                diaElement.classList.add('hoy');
            }
            
            const fecha = `${this.options.añoActual}-${String(this.options.mesActual + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
            const turnosDelDia = this.options.turnosPorDia[fecha] || 0;
            
            // Verificar si hay turnos disponibles
            if (this.options.diasDisponibles.includes(fecha)) {
                diaElement.classList.add('disponible');
            }
            
            const numero = document.createElement('span');
            numero.className = 'dia-numero';
            numero.textContent = dia;
            diaElement.appendChild(numero);
            
            if (turnosDelDia > 0) {
                const badge = document.createElement('span');
                badge.className = 'turnos-badge';
                badge.textContent = turnosDelDia;
                badge.title = `${turnosDelDia} turno(s)`;
                diaElement.appendChild(badge);
            }
            
            // Evento click
            diaElement.onclick = () => {
                // Remover selección anterior
                this.container.querySelectorAll('.calendario-dia.selected').forEach(d => {
                    d.classList.remove('selected');
                });
                
                diaElement.classList.add('selected');
                
                if (this.options.onDayClick) {
                    this.options.onDayClick(dia, this.options.mesActual, this.options.añoActual, fecha);
                }
            };
            
            calendar.appendChild(diaElement);
        }
        
        return calendar;
    }
    
    mesAnterior() {
        if (this.options.mesActual === 0) {
            this.options.mesActual = 11;
            this.options.añoActual--;
        } else {
            this.options.mesActual--;
        }
        this.render();
    }
    
    mesSiguiente() {
        if (this.options.mesActual === 11) {
            this.options.mesActual = 0;
            this.options.añoActual++;
        } else {
            this.options.mesActual++;
        }
        this.render();
    }
    
    irHoy() {
        const hoy = new Date();
        this.options.mesActual = hoy.getMonth();
        this.options.añoActual = hoy.getFullYear();
        this.render();
    }
    
    actualizarTurnos(turnosPorDia) {
        this.options.turnosPorDia = turnosPorDia;
        this.render();
    }
    
    actualizarDisponibilidad(diasDisponibles) {
        this.options.diasDisponibles = diasDisponibles;
        this.render();
    }
}
