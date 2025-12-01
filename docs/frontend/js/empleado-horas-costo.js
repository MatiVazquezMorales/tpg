const API_URL = "http://localhost:8000/api";

document.addEventListener("DOMContentLoaded", function () {
    inicializarSidebar();
    cargarUsuario();
    cargarCostos(); // Cargar costos automáticamente al entrar
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

async function cargarUsuario() {
    try {
        const res = await fetch(`${API_URL}/recursos/me`);
        if (!res.ok) throw new Error("Error al cargar usuario");
        
        const user = await res.json();
        document.querySelector('.profile-name').textContent = `${user.nombre} ${user.apellido}`;
        document.querySelector('.profile-role').textContent = user.rol_nombre || "Empleado";
    } catch (e) { 
        console.error(e);
        document.querySelector('.profile-name').textContent = "Error";
        document.querySelector('.profile-role').textContent = "No disponible";
    }
}

async function cargarCostos() {
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const costosContainer = document.getElementById('costos-container');
    
    // Ocultar errores y mostrar loading
    errorMessage.style.display = 'none';
    costosContainer.style.display = 'none';
    loading.style.display = 'block';
    
    try {
        // Paso 1: Obtener horas aprobadas de nuestro backend
        const horasRes = await fetch(`${API_URL}/horas-aprobadas`);
        if (!horasRes.ok) {
            throw new Error("Error al obtener horas aprobadas");
        }
        const horasAprobadas = await horasRes.json();
        
        if (!horasAprobadas || horasAprobadas.length === 0) {
            throw new Error("No hay horas aprobadas para calcular costos");
        }
        
        // Paso 2: Enviar horas aprobadas al módulo de finanzas para obtener costos por hora
        const costosRes = await fetch(`${API_URL}/costos/calcular`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(horasAprobadas)
        });
        
        if (!costosRes.ok) {
            const errorData = await costosRes.json().catch(() => ({ detail: "Error desconocido" }));
            throw new Error(errorData.detail || "Error al calcular costos");
        }
        
        const costosPorRol = await costosRes.json();
        
        // Paso 3: Obtener información de los recursos para mostrar nombres y roles
        const recursosRes = await fetch(`${API_URL}/recursos`);
        if (!recursosRes.ok) {
            throw new Error("Error al obtener información de recursos");
        }
        const recursos = await recursosRes.json();
        const recursosMap = {};
        recursos.forEach(r => {
            recursosMap[r.id] = r;
        });
        
        // Paso 4: Calcular costos combinando horas aprobadas con costos por hora
        const costosCalculados = calcularCostosPorRecurso(horasAprobadas, costosPorRol, recursosMap);
        
        // Paso 5: Renderizar los datos
        renderizarCostos(costosCalculados);
        
        loading.style.display = 'none';
        costosContainer.style.display = 'block';
        
    } catch (error) {
        console.error(error);
        loading.style.display = 'none';
        errorMessage.style.display = 'block';
        errorText.textContent = error.message || "Error al cargar los costos. Por favor, intente nuevamente.";
    }
}

function calcularCostosPorRecurso(horasAprobadas, costosPorRol, recursosMap) {
    // Crear un mapa de costos por rolId y período para búsqueda rápida
    const costosMap = {};
    costosPorRol.forEach(costoRol => {
        const rolId = costoRol.rolId;
        if (!costosMap[rolId]) {
            costosMap[rolId] = {};
        }
        costoRol.periodos.forEach(periodo => {
            const clave = `${periodo.anio}-${periodo.mes}`;
            costosMap[rolId][clave] = periodo.costo_hora;
        });
    });
    
    // Agrupar por recurso y calcular costos
    const costosPorRecurso = {};
    
    horasAprobadas.forEach(horas => {
        const recursoId = horas.recursoId;
        const recurso = recursosMap[recursoId];
        
        if (!recurso) return; // Saltar si no encontramos el recurso
        
        const rolId = recurso.rolId;
        if (!rolId || !costosMap[rolId]) return; // Saltar si no hay costo para este rol
        
        if (!costosPorRecurso[recursoId]) {
            costosPorRecurso[recursoId] = {
                recursoId: recursoId,
                nombre: `${recurso.nombre} ${recurso.apellido}`,
                rol: recurso.rol_nombre || 'Sin rol',
                horasTotales: 0,
                costoTotal: 0
            };
        }
        
        // Calcular costo para cada período
        horas.periodos.forEach(periodo => {
            const clave = `${periodo.anio}-${periodo.mes}`;
            const costoHora = costosMap[rolId][clave];
            
            if (costoHora !== undefined) {
                const horasPeriodo = periodo.horas_aprobadas;
                const costoPeriodo = horasPeriodo * costoHora;
                
                costosPorRecurso[recursoId].horasTotales += horasPeriodo;
                costosPorRecurso[recursoId].costoTotal += costoPeriodo;
    }
        });
    });
    
    return Object.values(costosPorRecurso);
}

function renderizarCostos(costosCalculados) {
    if (costosCalculados.length === 0) {
        document.getElementById('costos-container').innerHTML = '<div class="card"><p>No hay datos de costos disponibles.</p></div>';
        return;
    }
    
    // Calcular resumen general
    const totalEmpleados = costosCalculados.length;
    const costoTotal = costosCalculados.reduce((sum, c) => sum + c.costoTotal, 0);
    const promedioEmpleado = totalEmpleados > 0 ? costoTotal / totalEmpleados : 0;
    
    document.getElementById('total-empleados').textContent = totalEmpleados;
    document.getElementById('costo-total').textContent = formatearMoneda(costoTotal);
    document.getElementById('promedio-empleado').textContent = formatearMoneda(promedioEmpleado);
    
    // Ordenar por costo total descendente
    costosCalculados.sort((a, b) => b.costoTotal - a.costoTotal);
    
    // Renderizar tabla
    const tablaBody = document.getElementById('tabla-body');
    tablaBody.innerHTML = '';
    
    costosCalculados.forEach(costoRecurso => {
        const costoPorHora = costoRecurso.horasTotales > 0 
            ? costoRecurso.costoTotal / costoRecurso.horasTotales 
            : 0;
        
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #e2e8f0';
        row.innerHTML = `
            <td style="padding: 12px;">${costoRecurso.nombre}</td>
            <td style="padding: 12px;">${costoRecurso.rol}</td>
            <td style="text-align: right; padding: 12px;">${costoRecurso.horasTotales.toFixed(2)}</td>
            <td style="text-align: right; padding: 12px; font-weight: 600; color: #059669;">${formatearMoneda(costoRecurso.costoTotal)}</td>
            <td style="text-align: right; padding: 12px;">${formatearMoneda(costoPorHora)}</td>
        `;
        tablaBody.appendChild(row);
    });
}

function formatearMoneda(valor) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(valor);
}

// No se necesita setupListeners ya que los costos se cargan automáticamente
