# Modelo de Dominio - Carga de Horas

## Información del Documento

| Campo | Valor |
|-------|-------|
| **Módulo** | Carga de horas |
| **Squad** | Squad 3 |
| **Fecha de creación** | [23/10/2025] |
| **Última actualización** | [12/11/2025] |

## Diagrama del Modelo de Dominio

![Domain Model Diagram](/images/diagrams/domain-model-carga-de-horas.svg)

*Diagrama del modelo de dominio para el módulo carga de horas*

## Entidades del Dominio

### Cliente
- **Descripción:** [Descripción de la entidad]
- **Responsabilidades:** [Lista de responsabilidades]
- **Atributos principales:** 

    - **Nombre:** 
    - **País:** 

### Producto
- **Descripción:** [Descripción de la entidad]
- **Responsabilidades:** [Lista de responsabilidades]
- **Atributos principales:** 

    - **Nombre:** 
    - **Tipo de Contrato:** 
    - **Desceipción:** 

### Tareas
- **Descripción:** [Descripción de la entidad]
- **Responsabilidades:** [Lista de responsabilidades]
- **Atributos principales:** 

    - **Estado:** Puede estar no iniciada, abierta o cerrada.
    - **Tipo:** Puede ser de un proyecto, de licencia, soporte.
    - **Notas:** detalles y aclaraciones de la tarea. Por ejemplo, los ingenieros de soporte indicarían aquí el número del incidente.

### Horas invertidas
- **Descripción:** Define las horas que dedico un empleado a una tarea en una fecha específica
- **Responsabilidades:** ...
- **Atributos principales:** 

    - **Horas:** Son las horas invertidas en formato de horas y minutos


### Proyecto
- **Descripción:** ...
- **Responsabilidades:** ...
- **Atributos principales:**

    - **Tipo:** Puede ser de un proyecto de implementación o de desarrollo.

### Empleado
- **Descripción:** ...
- **Responsabilidades:** ...
- **Atributos principales:**

    - **Nombre:**


## Relaciones entre Entidades

| Entidad Origen | Relación | Entidad Destino | Descripción |
|----------------|----------|-----------------|-------------|
| [Entidad A] | [Tipo de relación] | [Entidad B] | [Descripción de la relación] |
| [Entidad B] | [Tipo de relación] | [Entidad C] | [Descripción de la relación] |

## Diccionario de Datos

| Entidad | Atributo | Descripción | Tipo Primitivo |
|---------|----------|-------------|----------------|
| Cliente | Nombre | Descripción del atributo | String |
| Cliente | País | Descripción del atributo | String |
| Producto | Nombre | [Descripción del atributo] | String |
| Producto | tipo de contrato | [Descripción del atributo] | Lista de valores |
| Producto | Descripción | [Descripción del atributo] | Text |
| Proyecto | Nombre | [Descripción del atributo] | String |
| Proyecto | Descripción | [Descripción del atributo] | text |
| Proyecto | País | [Descripción del atributo] | String |
| Proyecto | fecha de inicio | [Descripción del atributo] | Date |
| Proyecto | fecha de entrega | [Descripción del atributo] | Date |
| Proyecto | forma de facturación | [Descripción del atributo] | Lista de valores |
| Proyecto | tipo | [Descripción del atributo] | Lista de valores |
| tareas | estado | [Descripción del atributo] | Lista de valores |
| tareas | fecha de inicio | [Descripción del atributo] | Date |
| tareas | fecha de finalización | [Descripción del atributo] | Date |
| tareas | tipo | [Descripción del atributo] | Lista de valores |
| tareas | notas | [Descripción del atributo] | text |
| Empleado | Nombre | Descripción del atributo | String |
| Horas invertidas | fecha | [Descripción del atributo] | Date |
| Horas invertidas | horas | [Descripción del atributo] | int |

## Notas Adicionales

No hay notas adicionales

---

**Versión:** 1.0  
**Estado:** En revisión
