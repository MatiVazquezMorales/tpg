# Historias de Usuario - Carga de horas

## Información del Documento

| Campo | Valor |
|-------|-------|
| **Módulo** | Carga de horas |
| **Squad** | 3 |
| **Fecha de creación** | 30/10/2025 |
| **Última actualización** | 12/11/2025 |

## Matriz de Historias de Usuario

| Código | Título | Historia | Minutas | Feature File | Relaciones |
|--------|--------|----------|---------|--------------|------------|
| US-001 | Carga de horas en tareas| Como empleado Quiero registrar mis horas trabajadas en tareas Para reflejar mi dedicación semanal y cumplir con las 40 horas requeridas | [Minuta 7](/docs/meetings/meeting-20251002-minuta7-carga-de-horas.md) | [feature](/src/features/carga-horas/carga-horas.feature)| [US-002] |
| US-002 | Restricciones de tiempo y formato en carga de horas |  Como empleado Quiero que se validen las horas que registro Para cumplir con las políticas internas | [Minuta 7](/docs/meetings/meeting-20251002-minuta7-carga-de-horas.md) | [feature](/src/features/restricciones-horas/restricciones-horas.feature)| [US-001] |
| US-003 | Notificación a empleado por horas faltantes |  Como empleado Quiero recibir una notificación si no cargo mis 40 horas semanales Para completar la carga antes del cierre | [Minuta 7](/docs/meetings/meeting-20251002-minuta7-carga-de-horas.md) | [feature](/src/features/notificacion-carga-empleado/notificaciones-carga-empleado.feature)| [US-004] |
| US-004 | Notificación a gerente por horas faltantes de empleado |  Como gerente de operaciones Quiero recibir una notificación si un empleado no cargo sus 40 horas semanales Para saber en que se invirtieron las horas del empleado | [Minuta 7](/docs/meetings/meeting-20251002-minuta7-carga-de-horas.md) | [feature](/src/features/notificacion-carga-gerente/notificacion-carga-gerente.feature)| [US-003] |
| US-005 | Reporte de horas por empleado |  Como gerente de operaciones Quiero visualizar las horas cargadas por empleado y tarea Para evaluar la productividad y cumplimiento de las 40 horas | [Minuta 7](/docs/meetings/meeting-20251002-minuta7-carga-de-horas.md) | [feature](/src/features/reporte-horas/reporte-horas.feature)| |

## Estructura de Feature Files

Los feature files deben ubicarse en:
```
src/
├── features/
│   ├── [feature-name]/
│   │   ├── [feature-name].feature
│   │   └── step_definitions/
│   │       └── [feature-name]_steps
│   └── [another-feature]/
│       ├── [another-feature].feature
│       └── step_definitions/
│           └── [another-feature]_steps
```

## Formato de Feature Files

### Estructura básica de un .feature:
```gherkin
Feature: [Nombre de la funcionalidad]
  Como [tipo de usuario]
  Quiero [funcionalidad]
  Para [beneficio]

  Scenario: [Nombre del escenario]
    Given [condición inicial]
    When [acción del usuario]
    Then [resultado esperado]

  Scenario: [Otro escenario]
    Given [condición inicial]
    When [acción del usuario]
    Then [resultado esperado]
```

## Notas Adicionales

No hay notas Adicionales

---

**Versión:** 1.0  
**Estado:** Aprobado
