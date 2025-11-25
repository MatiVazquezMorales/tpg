# Diagrama de Contenedores - [Módulo de Carga de Horas PSA]

## Información del Documento

| Campo | Valor |
|-------|-------|
| **Módulo** | [Sistema de Carga de Horas PSA] |
| **Squad** | [squad 3] |
| **Fecha de creación** | [20/11/2025] |
| **Última actualización** | [20/11/2025] |

## Diagrama de Contenedores (C4 Nivel 2)

```mermaid
graph TB
    %% Usuarios externos
    subgraph "External Users"
        U1[Recurso PSA<br/>(Empleado)]
        U2[Administrador PSA]
    end
    
    %% Sistemas externos
    subgraph "External Systems"
        ES1[APIs Externas PSA<br/>(Mulesoft: Recursos, Proyectos, Tareas, Clientes, Roles)]
    end
    
    %% Módulo principal
    subgraph "Módulo Sistema de Carga de Horas PSA"
        subgraph "Contenedores de Aplicación"
            A1[Frontend Web<br/>(UI de Carga de Horas)]
            A2[Backend API REST<br/>(FastAPI)]
            A3[Servicio de Negocio<br/>(CargaHorasService)]
        end
        
        subgraph "Contenedores de Datos"
            D1[(Base de Datos<br/>PostgreSQL timesheet_db)]
            D2[(Cache en memoria<br/>(No implementado / Futuro))]
        end
    end
    
    %% Flujos usuario -> sistema
    U1 --> A1
    U2 --> A1
    
    %% Frontend -> Backend
    A1 --> A2
    
    %% Backend -> Servicio de negocio
    A2 --> A3
    
    %% Servicio de negocio / Backend -> Base de datos
    A3 --> D1
    
    %% Backend -> APIs externas
    A2 --> ES1
```

*Diagrama de contenedores del módulo [Sistema de Carga de Horas PSA] mostrando la arquitectura de contenedores*

## Descripción de Contenedores

### Contenedores de Aplicación

| Contenedor | Tecnología | Responsabilidades |
|-------------|------------|------------------|
| [Frontend Web (UI de Carga de Horas) (A1)] | [SPA/Web (framework a definir)] | [Interfaz de usuario para que los recursos y administradores consulten proyectos, tareas, calendario semanal, estadísticas y gestionen la carga de horas. Consume la API REST del backend.] |
| [Backend API REST (FastAPI) (A2)] | [Python + FastAPI] | [Exposición de endpoints REST] |
| [Servicio de Negocio CargaHorasService (A3)] | [Python] | [Implementar la lógica de negocio de la carga de horas] |

### Contenedores de Datos

| Contenedor | Tecnología | Responsabilidades |
|-------------|------------|------------------|
| [Base de Datos PostgreSQL timesheet_db (D1)] | [PostgreSQL] | [Almacenamiento persistente] |
| [Cache] | [Redis/Memcached] | [Almacenamiento temporal] |

## Interacciones entre Contenedores

| Origen | Destino | Protocolo | Descripción |
|--------|---------|-----------|-------------|
| [Recurso PSA / Administrador PSA (U1, U2)] | [Frontend Web (A1)] | [HTTP/REST] | [Los usuarios interactúan con la UI web para consultar proyectos, tareas, calendario, estadísticas y gestionar la carga de horas.] |
| [Frontend Web (A1)] | [Backend API REST (A2)] | [HTTP/gRPC] | [El frontend invoca endpoints REST del backend para obtener y actualizar información] |
| [Backend API REST] | [Servicio de Negocio CargaHorasService] | [PYTHON] | [La API delega en el servicio de negocio la validación de reglas, armado de respuestas complejas] |
| [Servicio de Negocio] | [Base de Datos] | [SQL/NoSQL] | [Consultas y transacciones] |
| [Backend API REST] | [APIs Externas PSA (Mulesoft)] | [HTTPS] | [Consulta de recursos, proyectos, tareas, clientes y roles para validar IDs, obtener nombres y armar respuestas enriquecidas] |
| [Servicio de Negocio] | [APIs Externas PSA (Mulesoft)] | [HTTPS] | [Validación de existencia y relación de proyecto/tarea/recurso antes de persistir una carga de horas.] |

## Notas Adicionales

[Información adicional sobre la arquitectura de contenedores, consideraciones técnicas, o cualquier detalle relevante]

---

**Versión:** 1.0  
**Estado:** [Borrador/En revisión/Aprobado]
