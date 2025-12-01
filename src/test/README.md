# Pruebas del Módulo

Esta sección contiene todos los entregables relacionados con las pruebas del módulo asignado.

## Estructura

```
src/
├── tests/
│   ├── unit/                   # P1. Pruebas Unitarias
│   │   └── README.md
│   └── acceptance/             # P2. Pruebas de Aceptación
│       └── README.md
├── features/                   # Feature Files Gherkin
│   ├── [feature-name]/
│   │   ├── [feature-name].feature
│   │   └── step_definitions/
│   │       └── [feature-name]_steps
│   └── [another-feature]/
│       ├── [another-feature].feature
│       └── step_definitions/
│           └── [another-feature]_steps
└── README.md                   # Este archivo
```

## Entregables

### P1. Pruebas Unitarias
- **Cobertura:** Mínimo 80% de cobertura de código
- **Frameworks:** JUnit, Jest, pytest, etc.
- **Estructura:** Un test por clase/método

### P2. Pruebas de Aceptación
- **Feature Files:** Escenarios Gherkin
- **Step Definitions:** Implementación de pasos
- **Frameworks:** Cucumber, Behave, etc.

## Cómo usar esta estructura

1. **Pruebas Unitarias:** Crear tests en `src/tests/unit/`
2. **Pruebas de Aceptación:** Crear feature files en `src/features/`
3. **Step Definitions:** Implementar en `src/features/[feature]/step_definitions/`
4. **Ejecutar pruebas:** Usar comandos del framework correspondiente

## Herramientas Recomendadas

- **Java:** JUnit + Cucumber
- **JavaScript:** Jest + Cucumber
- **Python:** pytest + Behave
- **C#:** NUnit + SpecFlow
