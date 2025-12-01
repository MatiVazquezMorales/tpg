const API_URL = "http://localhost:8000/api";

document.addEventListener("DOMContentLoaded", function () {
    inicializarSidebar();
    cargarUsuario();
    cargarMisProyectos();
    setupListeners();
});

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

function mostrarNotificacion() {
    const toast = document.getElementById('toast-exito');
    const closeIcon = document.getElementById('toast-close');
    
    if (!toast) return;

    toast.classList.add('active');

    let temporizador = setTimeout(() => {
        toast.classList.remove('active');
    }, 4000);

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

    if (msgElement) {
        msgElement.textContent = mensaje;
    }

    toast.classList.add('active');

    let temporizador = setTimeout(() => {
        toast.classList.remove('active');
    }, 5000);

    if (closeIcon) {
        closeIcon.onclick = () => {
            toast.classList.remove('active');
            clearTimeout(temporizador);
        };
    }
}

async function cargarUsuario() {
    try {
        const res = await fetch(`${API_URL}/recursos/me`);
        if (!res.ok) throw new Error("Error al cargar usuario");
        
        const user = await res.json();
        document.querySelector('.profile-name').textContent = `${user.nombre} ${user.apellido}`;
        document.querySelector('.profile-role').textContent = user.rol_nombre || "Empleado";
    } catch (e) { console.error(e); }
}

async function cargarMisProyectos() {
    const select = document.getElementById('select-proyecto');
    select.innerHTML = '<option value="">Cargando proyectos...</option>';

    try {
        const res = await fetch(`${API_URL}/proyectos`);
        if (!res.ok) throw new Error("Error cargando proyectos");
        
        const proyectos = await res.json();
        
        select.innerHTML = '<option value="">Seleccione un proyecto...</option>';
        
        select.dataset.proyectos = JSON.stringify(proyectos);

        proyectos.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.nombre;
            select.appendChild(opt);
        });

    } catch (error) {
        console.error(error);
        select.innerHTML = '<option value="">Error al cargar proyectos</option>';
    }
}

async function cargarTareasProyecto(proyectoId) {
    const select = document.getElementById('select-tarea');
    const card = document.getElementById('detalle-carga');
    
    select.innerHTML = '<option value="">Cargando tareas...</option>';
    select.disabled = true;
    card.style.display = 'none';

    try {
        const res = await fetch(`${API_URL}/proyectos/${proyectoId}/tareas`);
        if (!res.ok) throw new Error("Error cargando tareas");
        
        const tareas = await res.json();
        
        select.innerHTML = '<option value="">Seleccione una tarea...</option>';
        
        if (tareas.length === 0) {
            select.innerHTML = '<option value="">No hay tareas asignadas en este proyecto</option>';
            select.disabled = true;
        } else {
        select.dataset.tareas = JSON.stringify(tareas);
            select.disabled = false;

        tareas.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.nombre;
            select.appendChild(opt);
        });
        }

    } catch (error) {
        console.error(error);
        select.innerHTML = '<option value="">Error al cargar tareas</option>';
        select.disabled = true;
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
    
    // Listener para selección de proyecto
    document.getElementById('select-proyecto').addEventListener('change', (e) => {
        const proyectoId = e.target.value;
        const selectTarea = document.getElementById('select-tarea');
        const card = document.getElementById('detalle-carga');
        
        if (!proyectoId) {
            selectTarea.innerHTML = '<option value="">Primero seleccione un proyecto...</option>';
            selectTarea.disabled = true;
            card.style.display = 'none';
            return;
        }

        // Cargar tareas del proyecto seleccionado
        cargarTareasProyecto(proyectoId);
    });
    
    // Listener para selección de tarea
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

            // Obtener el proyecto seleccionado
            const proyectoId = document.getElementById('select-proyecto').value;
            if (proyectoId) {
                cargarInfoProyecto(proyectoId);
            } else {
                document.getElementById('info-proyecto-nombre').textContent = "Sin Proyecto";
            }

            card.style.display = 'block';
            
            const inputFecha = document.getElementById('input-fecha');
            if (!inputFecha.value) {
                inputFecha.valueAsDate = new Date();
            }
            const hoy = new Date();
            const yyyy = hoy.getFullYear();
            const mm = String(hoy.getMonth() + 1).padStart(2, '0');
            const dd = String(hoy.getDate()).padStart(2, '0');
            inputFecha.max = `${yyyy}-${mm}-${dd}`;
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
        const proyectoId = document.getElementById('select-proyecto').value;
        const tareaId = document.getElementById('select-tarea').value;
        
        const tareas = JSON.parse(document.getElementById('select-tarea').dataset.tareas || "[]");
        const tarea = tareas.find(t => t.id == tareaId);
        
        const fecha = document.getElementById('input-fecha').value;
        const horas = document.getElementById('input-horas').value;
        const notas = document.getElementById('input-notas').value;

        if (!proyectoId || !tareaId || !fecha || !horas) {
            mostrarError("Por favor complete los campos obligatorios (Proyecto, Tarea, Fecha, Horas)");
            return;
        }

        const fechaSeleccionada = new Date(fecha);
        const hoy = new Date();
        hoy.setHours(0,0,0,0);
        if (fechaSeleccionada > hoy) {
            mostrarError("No se puede registrar horas para días futuros.");
            return;
        }

        const horasNum = parseFloat(horas);
        if (horasNum > 24) {
            mostrarError("No se permite cargar más de 24 horas en un solo registro.");
            return;
        }

        if (horasNum <= 0) {
             mostrarError("Las horas deben ser mayores a 0.");
             return;
        }

        const payload = {
            tarea_id: tareaId,
            proyecto_id: proyectoId,
            fecha: fecha,
            horas: horasNum,
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
                mostrarNotificacion();
                
                document.getElementById('input-horas').value = "";
                document.getElementById('input-notas').value = "";
            } else {
                try {
                    const err = await res.json();
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