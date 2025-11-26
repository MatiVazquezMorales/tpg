const API_URL = "http://localhost:8000/api";

document.addEventListener("DOMContentLoaded", function () {
    inicializarSidebar();
    cargarUsuario();
    cargarMisTareas();
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

// --- Lógica de Notificaciones (Toasts) ---

function mostrarNotificacion() {
    const toast = document.getElementById('toast-exito');
    const closeIcon = document.getElementById('toast-close');
    
    if (!toast) return;

    // Mostrar
    toast.classList.add('active');

    // Ocultar automáticamente después de 4 segundos
    let temporizador = setTimeout(() => {
        toast.classList.remove('active');
    }, 4000);

    // Cerrar al hacer click en la X
    if (closeIcon) {
        closeIcon.onclick = () => {
            toast.classList.remove('active');
            clearTimeout(temporizador);
        };
    }
}

function mostrarError(mensaje) {
    const toast = document.getElementById('toast-error');
    const msgElement = document.getElementById('toast-error-msg');
    const closeIcon = document.getElementById('toast-error-close');
    
    if (!toast) return;

    // Actualizar el mensaje de error
    if (msgElement) {
        msgElement.textContent = mensaje;
    }

    // Mostrar
    toast.classList.add('active');

    // Ocultar automáticamente después de 5 segundos (un poco más largo para leer el error)
    let temporizador = setTimeout(() => {
        toast.classList.remove('active');
    }, 5000);

    // Cerrar al hacer click en la X
    if (closeIcon) {
        closeIcon.onclick = () => {
            toast.classList.remove('active');
            clearTimeout(temporizador);
        };
    }
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

async function cargarMisTareas() {
    const select = document.getElementById('select-tarea');
    select.innerHTML = '<option value="">Cargando tareas...</option>';

    try {
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

async function cargarInfoProyecto(proyectoId) {
    const nombreElem = document.getElementById('info-proyecto-nombre');
    const descElem = document.getElementById('info-proyecto-desc');
    
    nombreElem.textContent = "Cargando...";
    descElem.textContent = "...";

    try {
        const res = await fetch(`${API_URL}/proyectos/${proyectoId}`);
        if (!res.ok) throw new Error("Error cargando proyecto");
        
        const proyecto = await res.json();
        
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

        const tareas = JSON.parse(e.target.dataset.tareas || "[]");
        const tarea = tareas.find(t => t.id == tareaId);

        if (tarea) {
            document.getElementById('titulo-tarea').textContent = tarea.nombre;
            document.getElementById('info-tipo').textContent = "Desarrollo"; 
            
            const estadoElem = document.getElementById('info-estado');
            estadoElem.textContent = tarea.estado;
            
            estadoElem.className = ''; 
            if (tarea.estado === 'abierta' || tarea.estado === 'en curso') {
                estadoElem.style.color = 'green';
            } else {
                estadoElem.style.color = 'red';
            }

            if (tarea.proyectoId) {
                cargarInfoProyecto(tarea.proyectoId);
            } else {
                document.getElementById('info-proyecto-nombre').textContent = "Sin Proyecto";
            }

            card.style.display = 'block';
            
            const inputFecha = document.getElementById('input-fecha');
            if (!inputFecha.value) {
                inputFecha.valueAsDate = new Date();
            }
        }
    });

    // BOTÓN CANCELAR
    document.getElementById('btn-cancelar').addEventListener('click', () => {
        document.getElementById('input-horas').value = "";
        document.getElementById('input-notas').value = "";
    });

    // BOTÓN CARGAR HORAS
    document.getElementById('btn-cargar').addEventListener('click', async () => {
        const btn = document.getElementById('btn-cargar');
        const tareaId = document.getElementById('select-tarea').value;
        
        const tareas = JSON.parse(document.getElementById('select-tarea').dataset.tareas || "[]");
        const tarea = tareas.find(t => t.id == tareaId);
        
        const fecha = document.getElementById('input-fecha').value;
        const horas = document.getElementById('input-horas').value;
        const notas = document.getElementById('input-notas').value;

        // Validación local básica
        if (!tareaId || !fecha || !horas || !notas) {
            mostrarError("Por favor complete los campos obligatorios (Tarea, Fecha, Horas, Notas)");
            return;
        }

        const horasNum = parseFloat(horas);
        if (horasNum > 8) {
            mostrarError("No se permite cargar más de 8 horas en un solo registro.");
            return; // El 'return' detiene la ejecución, así no llama a la API.
        }
        // --------------------------------------------------

        // Validación 3: Horas negativas (por seguridad extra)
        if (horasNum <= 0) {
             mostrarError("Las horas deben ser mayores a 0.");
             return;
        }

        const payload = {
            tarea_id: tareaId,
            proyecto_id: tarea.proyectoId,
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
                // ¡Éxito! Mostramos el cartel verde
                mostrarNotificacion();
                
                // Limpiamos formulario
                document.getElementById('input-horas').value = "";
                document.getElementById('input-notas').value = "";
            } else {
                // Si hay error (ej: > 8 horas), mostramos el cartel rojo con el detalle
                try {
                    const err = await res.json();
                    // err.detail contiene el mensaje del backend ("No se pueden cargar más de 8 horas...")
                    mostrarError(err.detail || "Ocurrió un error desconocido");
                } catch (jsonError) {
                    mostrarError(`Error del servidor (${res.status}). Intente nuevamente.`);
                }
            }

        } catch (error) {
            console.error(error);
            mostrarError("Error de conexión con el servidor. Verifique que el backend esté corriendo.");
        } finally {
            btn.textContent = "Registrar Horas";
            btn.disabled = false;
        }
    });
}