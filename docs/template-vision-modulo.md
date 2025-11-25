# Visión del Módulo [Carga de horas]

## Información del Squad

| Campo | Valor |
|-------|-------|
| **Squad** | Squad 3 |
| **Módulo asignado** | Carga de horas |
| **Fecha de creación** | [DD/MM/YYYY] |
| **Última actualización** | [DD/MM/YYYY] |

## Resumen Ejecutivo

El módulo desarrolla la carga de horas en tareas. Las tareas pueden ser de desarrollo en proyectos, soporte o no relacionados con el cargo del usuario como puede ser un examen o examen medico

El proposito es saber en que se utilizaron las 40 horas semanales.
## Funcionalidades Principales

### Funcionalidades Core
- Cargar horas en tareas abiertas desde el lunes hasta el domingo inclusive
- Notificación al final de la semana si no se cargaron mínimo las 40 horas semanales
- Reporte de horas trabajadas en tareas por empleado
- Restricción de hasta 24 horas cargadas por día y no permitir carga de horas para fechas futuras.

### Funcionalidades Secundarias
- Carga masiva de horas
- Reporte de horas trabajadas por periodo de tiempo: mes, semana.

## Interacciones con Otros Módulos

### Módulos que Consumen este Módulo
| Módulo | Tipo de Interacción | Descripción |
|--------|-------------------|-------------|
| Finanzas | [API/Evento/Directa] | Las horas usadas por tarea |

### Módulos que este Módulo Consume
| Módulo | Tipo de Interacción | Descripción |
|--------|-------------------|-------------|
| [Módulo] | [API/Evento/Directa] | [Qué información necesita] |


## Consideraciones Técnicas

### Tecnologías Principales
- [Tecnología 1]
- [Tecnología 2]
- [Tecnología 3]

### Dependencias Externas
- [Dependencia 1]
- [Dependencia 2]

## Notas Adicionales

- Las horas cargadas con hasta dos decimales o en horas y minutos

- No se pueden cargar horas de fechas posteriores a la actual

- No se pueden modificar horas de tareas cerradas. Solo el gerente de operaciones

- No se pueden cargar más de 24 horas por día
---

**Versión:** 1.0  
**Estado:** [Borrador]
