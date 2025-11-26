const API_URL = "http://localhost:8000/api";
let fechaReferencia = new Date(); // Fecha actual para controlar la semana

document.addEventListener("DOMContentLoaded", function () {
    inicializarSidebar();
    cargarUsuario();
    cargarCalendario(); // Carga inicial
    setupNavegacion();
});

function inicializarSidebar() {
    const currentPage = location.pathname.split("/").pop();
    document.querySelectorAll('.sidebar .menu a').forEach(link => {
        if (link.getAttribute('href') === currentPage) link.classList.add('active');
    });
}

async function cargarUsuario() {
    try {
        const res = await fetch(`${API_URL}/recursos/me`);
        const user = await res.json();
        document.querySelector('.profile-name').textContent = `${user.nombre} ${user.apellido}`;
        document.querySelector('.profile-role').textContent = user.rol_nombre || "Empleado";
    } catch (e) { console.error(e); }
}

// --- Lógica del Calendario ---

function getLunes(d) {
    d = new Date(d);
    var day = d.getDay(),
        diff = d.getDate() - day + (day == 0 ? -6 : 1); // Ajustar cuando es domingo
    return new Date(d.setDate(diff));
}

function formatearFechaISO(date) {
    return date.toISOString().split('T')[0];
}

async function cargarCalendario() {
    const lunes = getLunes(fechaReferencia);
    const fechaStr = formatearFechaISO(lunes); // YYYY-MM-DD del lunes de esa semana
    
    // Actualizar etiqueta de la semana
    const finSemana = new Date(lunes);
    finSemana.setDate(lunes.getDate() + 6);
    const opcionesFecha = { month: 'short', day: 'numeric' };
    document.getElementById('week-label').textContent = 
        `${lunes.toLocaleDateString('es-ES', opcionesFecha)} - ${finSemana.toLocaleDateString('es-ES', opcionesFecha)}, ${lunes.getFullYear()}`;

    try {
        // Llamada al backend
        const res = await fetch(`${API_URL}/calendario?fecha=${fechaStr}`);
        if (!res.ok) throw new Error("Error al cargar calendario");
        
        const data = await res.json();
        renderizarCalendario(data);
        
    } catch (error) {
        console.error(error);
        alert("Error cargando datos del calendario");
    }
}

function renderizarCalendario(data) {
    // 1. Actualizar Headers (Lun 21, Mar 22...)
    data.dias.forEach((dia, index) => {
        const header = document.getElementById(`header-${index}`);
        if (header) {
            const fechaObj = new Date(dia.fecha + 'T00:00:00'); // Hack para evitar timezone offset
            header.querySelector('.day-number').textContent = fechaObj.getDate();
            
            // Resaltar si es hoy
            const hoy = new Date();
            if (fechaObj.toDateString() === hoy.toDateString()) {
                header.classList.add('highlight');
                header.querySelector('.day-number').classList.add('highlight');
            } else {
                header.classList.remove('highlight');
                header.querySelector('.day-number').classList.remove('highlight');
            }
        }
    });

    // 2. Limpiar columnas
    for (let i = 0; i < 7; i++) {
        const col = document.getElementById(`col-dia-${i}`);
        if (col) col.innerHTML = ''; 
    }

    // 3. Renderizar Eventos (Bloques de horas)
    data.dias.forEach((dia, index) => {
        const col = document.getElementById(`col-dia-${index}`);
        if (!col) return;

        // Variable para "apilar" visualmente las tareas. 
        // Asumimos que el día empieza a las 9:00 (fila 1)
        let filaActual = 1; 

        dia.entradas.forEach(entrada => {
            // Calculamos altura: 1 hora = 1 fila aprox (depende del CSS grid)
            // Si cargó 2.5 horas, redondeamos visualmente o usamos span
            const horas = parseFloat(entrada.horas);
            const span = Math.max(1, Math.round(horas)); // Mínimo ocupa 1 espacio

            const div = document.createElement('div');
            div.className = `event ${getColorPorProyecto(entrada.proyecto_nombre)}`;
            
            // Estilo Grid: Start / Span
            div.style.gridRow = `${filaActual} / span ${span}`;
            
            div.innerHTML = `
                <b>${entrada.proyecto_nombre}</b><br>
                <span style="font-size:0.9em">${entrada.tarea_nombre}</span><br>
                <span style="font-size:0.8em; opacity:0.8">${horas} hs</span>
            `;
            
            // Tooltip simple
            div.title = `${entrada.descripcion || ''}`;

            col.appendChild(div);

            // Avanzamos la fila para el siguiente bloque
            filaActual += span;
        });
    });

    // 4. Actualizar Total
    document.getElementById('total-horas-semana').textContent = data.total_semana;
}

// Función auxiliar para dar colores distintos según el proyecto
function getColorPorProyecto(nombreProyecto) {
    if (!nombreProyecto) return 'blue';
    const primerLetra = nombreProyecto.charCodeAt(0);
    if (primerLetra % 4 === 0) return 'blue';   // stylesEmpleado.css: .event.blue
    if (primerLetra % 4 === 1) return 'green';  // .event.green
    if (primerLetra % 4 === 2) return 'yellow'; // .event.yellow
    return 'cyan';                              // .event.cyan
}

function setupNavegacion() {
    document.getElementById('prev-week').addEventListener('click', () => {
        fechaReferencia.setDate(fechaReferencia.getDate() - 7);
        cargarCalendario();
    });
    
    document.getElementById('next-week').addEventListener('click', () => {
        fechaReferencia.setDate(fechaReferencia.getDate() + 7);
        cargarCalendario();
    });

    document.getElementById('btn-hoy').addEventListener('click', () => {
        fechaReferencia = new Date();
        cargarCalendario();
    });
}