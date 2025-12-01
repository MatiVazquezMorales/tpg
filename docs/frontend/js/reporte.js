const API_URL = "http://localhost:8000/api";
let fechaReferencia = new Date();
let recursoIdActual = null; // Para modo gerente

// Obtener recursoId de la URL si existe (modo gerente)
const urlParams = new URLSearchParams(window.location.search);
recursoIdActual = urlParams.get('recursoId');

document.addEventListener("DOMContentLoaded", function () {
    inicializarSidebar();
    cargarUsuario();
    cargarCalendario(); 
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
        let user;
        if (recursoIdActual) {
            // Modo gerente: obtener el recurso de la lista de recursos (que ya viene con rol_nombre)
            const res = await fetch(`${API_URL}/recursos`);
            if (!res.ok) throw new Error("Error cargando recursos");
            const recursos = await res.json();
            user = recursos.find(r => r.id === recursoIdActual);
            if (!user) throw new Error("Recurso no encontrado");
        } else {
            // Modo empleado: cargar información del usuario actual
            const res = await fetch(`${API_URL}/recursos/me`);
            if (!res.ok) throw new Error("Error cargando usuario");
            user = await res.json();
        }
        
        document.querySelector('.profile-name').textContent = `${user.nombre} ${user.apellido}`;
        document.querySelector('.profile-role').textContent = user.rol_nombre || "Empleado";
    } catch (e) { 
        console.error(e);
        document.querySelector('.profile-name').textContent = "Error";
        document.querySelector('.profile-role').textContent = "No disponible";
    }
}


function getLunes(d) {
    d = new Date(d);
    var day = d.getDay(),
        diff = d.getDate() - day + (day == 0 ? -6 : 1); 
    return new Date(d.setDate(diff));
}

function formatearFechaISO(date) {
    return date.toISOString().split('T')[0];
}

async function cargarCalendario() {
    const lunes = getLunes(fechaReferencia);
    const fechaStr = formatearFechaISO(lunes); 
    
    const finSemana = new Date(lunes);
    finSemana.setDate(lunes.getDate() + 6);
    const opcionesFecha = { month: 'short', day: 'numeric' };
    document.getElementById('week-label').textContent = 
        `${lunes.toLocaleDateString('es-ES', opcionesFecha)} - ${finSemana.toLocaleDateString('es-ES', opcionesFecha)}, ${lunes.getFullYear()}`;

    try {
        let url;
        if (recursoIdActual) {
            // Modo gerente: usar endpoint específico para el recurso
            url = `${API_URL}/recursos/${recursoIdActual}/calendario?fecha=${fechaStr}`;
        } else {
            // Modo empleado: usar endpoint del usuario actual
            url = `${API_URL}/calendario?fecha=${fechaStr}`;
        }
        
        const res = await fetch(url);
        if (!res.ok) throw new Error("Error al cargar calendario");
        
        const data = await res.json();
        renderizarCalendario(data);
        
    } catch (error) {
        console.error(error);
        alert("Error cargando datos del calendario");
    }
}

function renderizarCalendario(data) {
    data.dias.forEach((dia, index) => {
        const header = document.getElementById(`header-${index}`);
        if (header) {
            const fechaObj = new Date(dia.fecha + 'T00:00:00'); 
            header.querySelector('.day-number').textContent = fechaObj.getDate();
            
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

    for (let i = 0; i < 7; i++) {
        const col = document.getElementById(`col-dia-${i}`);
        if (col) col.innerHTML = ''; 
    }

    data.dias.forEach((dia, index) => {
        const col = document.getElementById(`col-dia-${index}`);
        if (!col) return;

        let filaActual = 1; 

        dia.entradas.forEach(entrada => {
            
            const horas = parseFloat(entrada.horas);
            const span = Math.max(1, Math.round(horas)); 

            const div = document.createElement('div');
            div.className = `event ${getColorPorProyecto(entrada.proyecto_nombre)}`;
            
            div.style.gridRow = `${filaActual} / span ${span}`;
            
            div.innerHTML = `
                <b>${entrada.proyecto_nombre}</b><br>
                <span style="font-size:0.9em">${entrada.tarea_nombre}</span><br>
                <span style="font-size:0.8em; opacity:0.8">${horas} hs</span>
            `;
            
            div.title = `${entrada.descripcion || ''}`;

            col.appendChild(div);

            filaActual += span;
        });
    });

    document.getElementById('total-horas-semana').textContent = data.total_semana;
}

function getColorPorProyecto(nombreProyecto) {
    if (!nombreProyecto) return 'blue';
    const primerLetra = nombreProyecto.charCodeAt(0);
    if (primerLetra % 4 === 0) return 'blue'; 
    if (primerLetra % 4 === 1) return 'green';  
    if (primerLetra % 4 === 2) return 'yellow'; 
    return 'cyan';                              
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