# Minuta de Reunión - [Reunión con Augusto Aguante (Jefe de Soporte)]

## Información de la Reunión

| Campo | Valor |
|-------|-------|
| **Fecha de convocatoria** | [02/10/2025] |
| **Hora de convocatoria** | [21:00] |
| **Fecha de reunión** | [02/10/2025] |
| **Hora de inicio** | [21:00] |
| **Hora de finalización** | [21:30] |
| **Lugar** | [Virtual - Zoom] |
| **Modalidad** | [Remota] |
| **Duración** | [30 minutos] |
| **Redactor** | [Favio Condori] |

## Asistentes

| Nombre | Rol | Asistencia |
|--------|-----|------------|
| [Gonzalo Garcia] | [Desarrollador] | ✅ Presente |
| [Emilio Michelli] | [Desarrollador] | ✅ Presente |
| [Favio Condori] | [Desarrollador] | ✅ Presente |
| [Matias Vazquez Morales] | [Desarrollador] | ✅ Presente |
| [Alexis Torrez Vargas] | [Desarrollador] | ✅ Presente |

## Resumen Ejecutivo

Se definieron los requerimientos para el sistema de gestión de soporte técnico orientado a mejorar la trazabilidad y eficiencia en la resolución de incidentes. Se estableció la necesidad de automatizar la identificación de versiones de productos y módulos customizados de los clientes. El sistema debe gestionar tickets con información completa incluyendo categorización por impacto y criticidad, registro inmutable de interacciones con el cliente, y mapeo con tareas de resolución. Se requiere implementar un sistema de priorización inteligente que considere SLA, prioridad y severidad, junto con temporizadores visuales para evitar incumplimientos.

## Detalle de la Minuta

### 1. [Identificación Automática de Configuración del Cliente]
El sistema debe reportar automáticamente qué versión del producto está usando cada cliente y cuáles módulos tiene customizados. Esta información permitirá al equipo de soporte identificar rápidamente qué manuales o código debe consultar para resolver incidentes.

### 2. [Estructura y Categorización de Tickets]
Los tickets deben incluir: número del cliente, descripción, categoría (problema o incidente), nivel de impacto, nivel de criticidad, y tipo de acuerdo de servicio. Se requiere un campo inmutable con el registro cronológico de todos los sucesos, conversaciones y envíos al cliente. Las prioridades P1/S1 se tratarán de forma diferente según el acuerdo de servicio específico de cada cliente.

### 3. [Gestión de Resolución y Carga Horaria]
Se implementará un mapeo entre los incidentes abiertos y las tareas creadas para solucionarlos, permitiendo medir el avance de la resolución. El personal podrá cargar horas trabajadas relacionadas con las tareas asociadas a cada incidente. Cada incidente debe mostrar un temporizador indicando el tiempo restante antes de incumplir el SLA.

### 4. [Filtros, Priorización y Agrupación de Incidentes]
Se requieren filtros por cliente y por producto para identificar cuáles tienen más incidentes. El orden predeterminado será por prioridad y severidad, balanceado con el tiempo restante para cumplir el SLA. Por ejemplo, un P3/S3 con 10 minutos para incumplir no se priorizará sobre un P1/S1. El sistema debe permitir agrupar problemas relacionados.

## Compromisos Asumidos

| Responsable | Compromiso | Fecha límite | Estado |
|-------------|------------|--------------|--------|
| [Equipo de Desarrollo] | [Implementar reporte automático de versiones y customizaciones] | [Por definir] | [Pendiente] |
| [Equipo de Desarrollo] | [Desarrollar estructura completa de tickets con categorización] | [Por definir] | [Pendiente] |
| [Equipo de Desarrollo] | [Crear registro inmutable de interacciones con clientes] | [Por definir] | [Pendiente] |
| [Equipo de Desarrollo] | [Implementar mapeo entre incidentes y tareas de resolución] | [Por definir] | [Pendiente] |
| [Equipo de Desarrollo] | [Desarrollar temporizadores de SLA en cada incidente] | [Por definir] | [Pendiente] |
| [Equipo de Desarrollo] | [Crear sistema de priorización inteligente con filtros] | [Por definir] | [Pendiente] |

## Próximos Pasos

- [ ] [Definir protocolo de reporte automático desde sistemas de clientes] - Responsable: [Por definir] - Fecha: [Por definir]
- [ ] [Establecer taxonomía de categorías, impactos y criticidades] - Responsable: [Por definir] - Fecha: [Por definir]
- [ ] [Diseñar algoritmo de priorización balanceado con SLA] - Responsable: [Por definir] - Fecha: [Por definir]
- [ ] [Definir estructura de mapeo incidente-tarea] - Responsable: [Por definir] - Fecha: [Por definir]
- [ ] [Establecer reglas de agrupación de problemas relacionados] - Responsable: [Por definir] - Fecha: [Por definir]
- [ ] [Configurar temporizadores según acuerdos de servicio por cliente] - Responsable: [Por definir] - Fecha: [Por definir]

## Próxima Reunión

| Campo | Valor |
|-------|-------|
| **Fecha propuesta** | [Por definir] |
| **Hora propuesta** | [Por definir] |
| **Lugar** | [Virtual - Zoom] |
| **Temas a tratar** | [Revisión de diseño del sistema de gestión de soporte] |

## Observaciones Adicionales

[Se destacó la importancia de un sistema de priorización inteligente que no solo considere la severidad del incidente sino también el tiempo restante para el cumplimiento del SLA, evitando así incumplimientos que afecten la relación con los clientes.]

---

**Fecha de creación:** [06/10/2025]  
**Última actualización:** [06/10/2025]