# Requisitos del Módulo

Esta sección contiene todos los entregables relacionados con el análisis y especificación de requisitos del módulo asignado.

## Estructura

```
requirements/
├── stakeholders/           # R1. Análisis de Interesados
│   ├── template-organigrama.md     # R1.1 Organigrama
│   └── template-onion-model.md     # R1.2 Onion Model
├── specifications/        # R3. Especificación de Requisitos
│   ├── template-user-stories.md    # R3.1 Historias de usuario y escenarios Gherkin
│   └── template-traceability-matrix.md    # R3.2 Matriz de Trazabilidad
├── analysis/              # R4. Modelo de Análisis
│   ├── template-context-diagram.md # R4.1 Diagrama de Contexto (C4 nivel 1)
│   └── template-domain-model.md    # R4.2 Modelo de Dominio + Diccionario
├── prototypes/            # R4.3 Prototipos de interfaz
│   └── template-ui-prototypes.md     # Prototipos de HDU significativas
└── README.md              # Este archivo
```

## Entregables

### R1. Análisis de Interesados
- **R1.1 Organigrama:** Estructura organizacional y roles
- **R1.2 Onion Model:** Modelo de capas de interesados

### R2. Minutas de Reunión
- Ubicadas en `/docs/meetings/`
- Usar template: `template-meeting-AAAAMMDD-title.md`

### R3. Especificación de Requisitos
- **R3.1 Historias de usuario:** En formato Gherkin (feature files)
- **R3.2 Matriz de Trazabilidad:** HDU vs. minutas

### R4. Modelo de Análisis
- **R4.1 Diagrama de Contexto:** C4 nivel 1
- **R4.2 Modelo de Dominio:** Entidades y diccionario de datos
- **R4.3 Prototipos:** Interfaz de usuario para HDU significativas

## Cómo usar esta estructura

1. **Copiar templates:** Usar los archivos template-* como base
2. **Completar información:** Seguir las instrucciones en cada template
3. **Mantener actualizado:** Revisar y actualizar según evolucione el proyecto
4. **Versionar cambios:** Usar commits descriptivos para cada entregable
