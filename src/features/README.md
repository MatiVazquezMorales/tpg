# Feature Files Gherkin

## Información del Módulo

| Campo | Valor |
|-------|-------|
| **Módulo** | [Nombre del módulo] |
| **Squad** | [Nombre del squad] |
| **Fecha de creación** | [DD/MM/YYYY] |
| **Última actualización** | [DD/MM/YYYY] |

## Estructura de Feature Files

```
src/features/
├── [feature-name]/
│   ├── [feature-name].feature
│   └── step_definitions/
│       └── [feature-name]_steps
└── [another-feature]/
    ├── [another-feature].feature
    └── step_definitions/
        └── [another-feature]_steps
```

## Feature Files por Historia de Usuario

| Código HDU | Feature File | Escenarios | Estado |
|------------|--------------|------------|--------|
| US-001 | [feature-name].feature | [Número] | [Completado/En progreso] |
| US-002 | [another-feature].feature | [Número] | [Completado/En progreso] |

## Formato de Feature Files

### Estructura básica:
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

### Step Definitions:
- **Ubicación:** `src/features/[feature-name]/step_definitions/`
- **Formato:** `[feature-name]_steps`
- **Implementación:** Según el framework utilizado

## Frameworks Recomendados

- **Java:** Cucumber + JUnit
- **JavaScript:** Cucumber + Jest
- **Python:** Behave + pytest
- **C#:** SpecFlow + NUnit

## Notas Adicionales

[Información adicional sobre los feature files, convenciones de naming, o cualquier detalle relevante]

---

**Versión:** 1.0  
**Estado:** [Borrador/En revisión/Aprobado]
