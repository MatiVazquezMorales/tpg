# Diagrama de Componentes - [Sistema de Carga de Horas PSA
]

## Información del Documento

| Campo | Valor |
|-------|-------|
| **Módulo** | [Sistema de Carga de Horas PSA
] |
| **Squad** | [squad 3] |
| **Fecha de creación** | [20/11/2025] |
| **Última actualización** | [20/11/2025] |

## Diagrama de Componentes (C4 Nivel 3)

```mermaid
graph TB
    %% Contenedor API REST (FastAPI)
    subgraph "API REST Container (FastAPI)"
        C1[Controller Layer<br/>(Endpoints FastAPI en main.py)]
        C2[Service Layer<br/>(Uso de CargaHorasService)]
        C3[DB Session Provider<br/>(database.get_db)]
    end
    
    %% Servicio de Negocio
    subgraph "Servicio de Negocio (services.py)"
        C4[Business Logic<br/>(CargaHorasService)]
        C5[Validation Service<br/>(validar_horas_diarias)]
        C6[Aggregation Service<br/>(Calendario y Estadísticas)]
    end
    
    %% Servicio de Datos / Integraciones
    subgraph "Servicio de Datos e Integraciones"
        C7[Data Access Layer<br/>(SQL sobre tabla carga_horas)]
        C8[Cache Manager en Memoria<br/>(proyectos_cache / tareas_cache)]
        C9[External API Client<br/>(external_apis.api_client)]
    end
    
    %% Sistemas externos
    subgraph "External Systems"
        ES1[APIs Externas PSA<br/>(Recursos/Proyectos/Tareas/Clientes/Roles)]
        DB1[(Base de Datos PostgreSQL<br/>timesheet_db.carga_horas)]
        CACHE1[(Cache Persistente<br/>(Futuro))]
    end

    %% Relaciones internas
    C1 --> C2
    C2 --> C3
    C2 --> C4
    C4 --> C5
    C4 --> C6
    C3 --> C7
    C7 --> C8
    C7 --> C9
    C7 --> DB1
    C8 --> CACHE1
    C9 --> ES1
```

*Diagrama de componentes del módulo [Nombre del módulo] mostrando la estructura interna de componentes*

## Descripción de Componentes

### Capa de Controladores

| Componente | Responsabilidades | Tecnología |
|-----------|------------------|------------|
| Endpoints FastAPI (`main.py`) | Manejo de requests HTTP REST, definición de rutas (`/api/proyectos`, `/api/horas`, `/api/calendario`, `/api/estadisticas`, `/api/recursos/me`, `/health`, `/`) y construcción de respuestas/errores (`HTTPException`). | Python, FastAPI |
| Proveedor de sesión de BD (`database.get_db`) | Proveer instancias de `Session` de SQLAlchemy a los endpoints mediante inyección de dependencias (`Depends(get_db)`), gestionando el ciclo de vida de la conexión. | Python, SQLAlchemy, FastAPI DI |
| Resolución de usuario actual (`get_current_user_id` / `config.get_recurso_id_desarrollo`) | Resolver el `recurso_id` del usuario actual de desarrollo y exponerlo a los endpoints para filtrar datos y validar permisos sobre las cargas de horas. | Python |

---

### Capa de Servicios

| Componente | Responsabilidades | Tecnología |
|-----------|------------------|------------|
| `CargaHorasService` (Business Logic) | Lógica de negocio principal del módulo: creación de cargas de horas, actualización de registros, obtención de calendario semanal, cálculo de estadísticas del recurso y coordinación con BD y APIs externas. | Python |
| `validar_horas_diarias` (Validation Service) | Validar que el total de horas por día y por recurso no supere las 24 horas, calculando el acumulado desde la tabla `carga_horas` y retornando `(es_valido, total_actual)`. | Python, SQLAlchemy (consultas SQL) |
| Servicios de agregación (`obtener_calendario_semanal`, `obtener_estadisticas_recurso`) | Construir estructuras agregadas de negocio: calendario semanal (lunes–domingo con entradas por proyecto/tarea) y estadísticas del recurso (horas del mes, semana, proyectos activos, promedio diario). | Python, SQLAlchemy |

---

### Capa de Acceso a Datos

| Componente | Responsabilidades | Tecnología |
|-----------|------------------|------------|
| Data Access Layer sobre `carga_horas` | Ejecutar consultas SQL crudas (`INSERT`, `UPDATE`, `DELETE`, `SELECT`, `SUM`, `COUNT DISTINCT`, `AVG`) contra la tabla `carga_horas` usando `db.execute(text(...))` y `commit()`. | Python, SQLAlchemy, PostgreSQL |
| Cache Manager en memoria (`proyectos_cache`, `tareas_cache`) | Cachear en memoria la información de proyectos y tareas al construir el calendario semanal, evitando múltiples llamadas a las APIs externas para los mismos IDs. | Python (diccionarios en memoria) |
| Cliente de APIs externas (`external_apis.api_client`) | Comunicar el sistema con las APIs externas PSA (Mulesoft) para obtener recursos, proyectos, tareas, clientes y roles, y validar la existencia y relación de estos elementos. | Python, HTTP/REST |
| Base de Datos PostgreSQL (`timesheet_db`) | Almacenamiento persistente de las cargas de horas y aplicación de restricciones de integridad (PK, índices, `CHECK` de horas y trigger `validar_horas_diarias`). | PostgreSQL + extensión `pgcrypto` |

---

## Interacciones entre Componentes

| Origen | Destino | Tipo | Descripción |
|--------|---------|------|-------------|
| Endpoints FastAPI (`main.py`) | `CargaHorasService` | Llamada directa | Delegan la lógica de negocio (creación/actualización/eliminación de cargas, calendario y estadísticas) al servicio de dominio. |
| Endpoints FastAPI (`main.py`) | Proveedor de sesión de BD (`get_db`) | Inyección de dependencia | Obtienen una sesión de base de datos por request mediante `Depends(get_db)` para ejecutar operaciones sobre `carga_horas`. |
| Endpoints FastAPI (`main.py`) | Resolución de usuario actual (`get_current_user_id`) | Llamada directa | Obtienen el `recurso_id` a partir de la configuración para filtrar consultas y validar permisos. |
| `CargaHorasService` | Data Access Layer (`carga_horas`) | Llamada directa | Ejecuta las consultas e inserciones SQL necesarias para guardar y leer las cargas de horas y estadísticas. |
| `CargaHorasService` | `validar_horas_diarias` | Llamada directa | Utiliza el servicio de validación para asegurar la regla de negocio de máximo 24 horas diarias antes de persistir cambios. |
| `CargaHorasService` | Cliente de APIs externas (`external_apis.api_client`) | Llamada directa | Valida existencia y relación de proyectos, tareas y recursos, y enriquece las respuestas con datos externos (nombres, datos del recurso, etc.). |
| Cliente de APIs externas (`external_apis.api_client`) | APIs Externas PSA (Mulesoft) | HTTP/REST | Realiza requests a los endpoints externos configurados en `config.py` (`RECURSOS_API`, `PROYECTOS_API`, `TAREAS_API`, `CLIENTES_API`, `ROLES_API`). |
| Data Access Layer (`carga_horas`) | Base de Datos PostgreSQL | SQL | Envía consultas SQL para leer/escribir en la tabla `carga_horas`, utilizando índices y el trigger de validación en la BD. |
| Cache Manager en memoria | Cliente de APIs externas | Llamada directa | Solo recurre al cliente externo cuando un `proyecto_id` o `tarea_id` no está presente en el cache local, y luego almacena la respuesta. |

---

## Notas Adicionales

---

**Versión:** 1.0  
**Estado:** [Borrador/En revisión/Aprobado]
