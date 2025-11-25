# Diagrama de Contenedores - [Nombre del Módulo]

## Información del Documento

| Campo | Valor |
|-------|-------|
| **Módulo** | [Nombre del módulo] |
| **Squad** | [Nombre del squad] |
| **Fecha de creación** | [DD/MM/YYYY] |
| **Última actualización** | [DD/MM/YYYY] |

## Diagrama de Contenedores (C4 Nivel 2)

```mermaid
graph TB
    subgraph "External Users"
        U1[Usuario Web]
        U2[Usuario Móvil]
        U3[Administrador]
    end
    
    subgraph "External Systems"
        ES1[Sistema de Autenticación]
        ES2[Sistema de Pagos]
        ES3[Base de Datos Externa]
    end
    
    subgraph "Módulo Nombre del Módulo"
        subgraph "Contenedores de Aplicación"
            A1[API REST]
            A2[Servicio de Negocio]
            A3[Servicio de Datos]
        end
        
        subgraph "Contenedores de Datos"
            D1[(Base de Datos)]
            D2[(Cache)]
        end
    end
    
    U1 --> A1
    U2 --> A1
    U3 --> A1
    A1 --> A2
    A2 --> A3
    A3 --> D1
    A3 --> D2
    A1 --> ES1
    A2 --> ES2
    A3 --> ES3
```

*Diagrama de contenedores del módulo [Nombre del módulo] mostrando la arquitectura de contenedores*

## Descripción de Contenedores

### Contenedores de Aplicación

| Contenedor | Tecnología | Responsabilidades |
|-------------|------------|------------------|
| [API REST] | [Node.js/Spring Boot/etc.] | [Exposición de endpoints REST] |
| [Servicio de Negocio] | [Java/Python/etc.] | [Lógica de negocio] |
| [Servicio de Datos] | [Java/Python/etc.] | [Acceso a datos] |

### Contenedores de Datos

| Contenedor | Tecnología | Responsabilidades |
|-------------|------------|------------------|
| [Base de Datos] | [PostgreSQL/MySQL/MongoDB] | [Almacenamiento persistente] |
| [Cache] | [Redis/Memcached] | [Almacenamiento temporal] |

## Interacciones entre Contenedores

| Origen | Destino | Protocolo | Descripción |
|--------|---------|-----------|-------------|
| [API REST] | [Servicio de Negocio] | [HTTP/REST] | [Solicitudes de lógica de negocio] |
| [Servicio de Negocio] | [Servicio de Datos] | [HTTP/gRPC] | [Acceso a datos] |
| [Servicio de Datos] | [Base de Datos] | [SQL/NoSQL] | [Consultas y transacciones] |

## Notas Adicionales

[Información adicional sobre la arquitectura de contenedores, consideraciones técnicas, o cualquier detalle relevante]

---

**Versión:** 1.0  
**Estado:** [Borrador/En revisión/Aprobado]
