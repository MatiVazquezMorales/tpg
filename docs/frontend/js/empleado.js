// docs/frontend/js/empleado.js

const API_URL = "http://localhost:8000/api";

document.addEventListener("DOMContentLoaded", function () {
    inicializarSidebar();
    cargarUsuario();
    cargarMisTareas(); // <-- Nuevo punto de entrada: Cargar tareas directamente
    setupListeners();
});

// --- Lógica de UI (Sidebar) ---
function inicializarSidebar() {
    const currentPage = location.pathname.split("/").pop();
    document.querySelectorAll('.sidebar .menu a').forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// --- Lógica de Datos ---

async function cargarUsuario() {
    try {
        const res = await fetch(`${API_URL}/recursos/me`);
        if (!res.ok) throw new Error("Error al cargar usuario");
        
        const user = await res.json();
        document.querySelector('.profile-name').textContent = `${user.nombre} ${user.apellido}`;
        document.querySelector('.profile-role').textContent = user.rol_nombre || "Empleado";
    } catch (e) { console.error(e); }
}

// 1. CARGAR TODAS LAS TAREAS ASIGNADAS (Nuevo flujo)
async function cargarMisTareas() {
    const select = document.getElementById('select-tarea');
    select.innerHTML = '<option value="">Cargando tareas...</option>';

    try {
        // Consume el endpoint nuevo que creamos en el backend
        const res = await fetch(`${API_URL}/tareas/me`);
        if (!res.ok) throw new Error("Error cargando tareas");
        
        const tareas = await res.json();
        
        select.innerHTML = '<option value="">Seleccione una tarea...</option>';
        
        // Guardamos las tareas en el dataset para poder leer el proyectoId después
        select.dataset.tareas = JSON.stringify(tareas);

        tareas.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.nombre;
            select.appendChild(opt);
        });

    } catch (error) {
        console.error(error);
        select.innerHTML = '<option value="">Error al cargar tareas</option>';
    }
}

// 2. BUSCAR INFO DEL PROYECTO (Se llama al seleccionar tarea)
async function cargarInfoProyecto(proyectoId) {
    const nombreElem = document.getElementById('info-proyecto-nombre');
    const descElem = document.getElementById('info-proyecto-desc');
    
    nombreElem.textContent = "Cargando...";
    descElem.textContent = "...";

    try {
        const res = await fetch(`${API_URL}/proyectos/${proyectoId}`);
        if (!res.ok) throw new Error("Error cargando proyecto");
        
        const proyecto = await res.json();
        
        // Actualizamos el bloque de información del proyecto en el HTML
        nombreElem.textContent = proyecto.nombre;
        descElem.textContent = proyecto.descripcion;
        
    } catch (error) {
        console.error(error);
        nombreElem.textContent = "No disponible";
        descElem.textContent = "No se pudo cargar la información del proyecto.";
    }
}

function setupListeners() {
    
    // AL CAMBIAR LA SELECCIÓN DE TAREA
    document.getElementById('select-tarea').addEventListener('change', (e) => {
        const tareaId = e.target.value;
        const card = document.getElementById('detalle-carga');
        
        if (!tareaId) {
            card.style.display = 'none';
            return;
        }

        // Recuperamos el objeto tarea completo desde la memoria
        const tareas = JSON.parse(e.target.dataset.tareas || "[]");
        const tarea = tareas.find(t => t.id == tareaId);

        if (tarea) {
            // 1. Mostrar detalles de la tarea
            document.getElementById('titulo-tarea').textContent = tarea.nombre;
            document.getElementById('info-tipo').textContent = "Desarrollo"; // Ajustar si la API trae 'tipo'
            
            const estadoElem = document.getElementById('info-estado');
            estadoElem.textContent = tarea.estado;
            
            // Estilo del estado
            estadoElem.className = ''; // Limpiar
            if (tarea.estado === 'abierta' || tarea.estado === 'en curso') {
                estadoElem.style.color = 'green';
            } else {
                estadoElem.style.color = 'red';
            }

            // 2. Cargar información del Proyecto Automáticamente
            if (tarea.proyectoId) {
                cargarInfoProyecto(tarea.proyectoId);
            } else {
                document.getElementById('info-proyecto-nombre').textContent = "Sin Proyecto";
            }

            // 3. Mostrar el formulario
            card.style.display = 'block';
            
            // Poner fecha de hoy por defecto si está vacío
            const inputFecha = document.getElementById('input-fecha');
            if (!inputFecha.value) {
                inputFecha.valueAsDate = new Date();
            }
        }
    });

    // BOTÓN CANCELAR / LIMPIAR
    document.getElementById('btn-cancelar').addEventListener('click', () => {
        document.getElementById('input-horas').value = "";
        document.getElementById('input-notas').value = "";
        // Opcional: Resetear select
        // document.getElementById('select-tarea').value = "";
        // document.getElementById('detalle-carga').style.display = "none";
    });

    // BOTÓN CARGAR HORAS
    document.getElementById('btn-cargar').addEventListener('click', async () => {
        const btn = document.getElementById('btn-cargar');
        const tareaId = document.getElementById('select-tarea').value;
        
        // Buscamos la tarea de nuevo para sacar el ID del proyecto (necesario para el backend)
        const tareas = JSON.parse(document.getElementById('select-tarea').dataset.tareas || "[]");
        const tarea = tareas.find(t => t.id == tareaId);
        
        const fecha = document.getElementById('input-fecha').value;
        const horas = document.getElementById('input-horas').value;
        const notas = document.getElementById('input-notas').value;

        // Validaciones
        if (!tareaId || !fecha || !horas) {
            alert("Por favor complete los campos obligatorios (Tarea, Fecha, Horas)");
            return;
        }

        // Armamos el paquete para enviar
        const payload = {
            tarea_id: tareaId,
            proyecto_id: tarea.proyectoId, // <-- Dato crucial obtenido internamente
            fecha: fecha,
            horas: parseFloat(horas),
            descripcion: notas
        };

        try {
            btn.textContent = "Guardando...";
            btn.disabled = true;

            const res = await fetch(`${API_URL}/horas`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                alert("¡Carga de horas registrada con éxito!");
                // Limpiar formulario
                document.getElementById('input-horas').value = "";
                document.getElementById('input-notas').value = "";
            } else {
                const err = await res.json();
                alert("Error al cargar: " + (err.detail || "Error desconocido"));
            }

        } catch (error) {
            console.error(error);
            alert("Error de conexión con el servidor.");
        } finally {
            btn.textContent = "Registrar Horas";
            btn.disabled = false;
        }
    });
}