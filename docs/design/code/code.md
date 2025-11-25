# Diagrama de Código - [Modulo de Carga de Horas PSA]

## Información del Documento

| Campo | Valor |
|-------|-------|
| **Módulo** | [Carga de Horas PSA] |
| **Squad** | [Squad 3] |
| **Fecha de creación** | [20/11/2025] |
| **Última actualización** | [20/11/2025] |

## Diagrama de Código (C4 Nivel 4)

```mermaid
classDiagram
    class AppConfig {
        +DATABASE_URL: str
        +RECURSO_ID_DESARROLLO: str
        +RECURSOS_API: str
        +CLIENTES_API: str
        +TAREAS_API: str
        +ROLES_API: str
        +PROYECTOS_API: str
        +PORT: int
        +LOG_LEVEL: str
        +CORS_ORIGINS: List[str]
        +API_TIMEOUT: int
        +get_recurso_id_desarrollo(): UUID
    }

    class HorasController {
        +obtener_mis_proyectos()
        +obtener_tareas_proyecto(proyecto_id: UUID)
        +obtener_calendario(fecha: date, db: Session)
        +cargar_horas(carga: CargaHoraCreate, db: Session)
        +actualizar_horas(carga_id: UUID, carga: CargaHoraUpdate, db: Session)
        +eliminar_horas(carga_id: UUID, db: Session)
        +obtener_estadisticas(db: Session)
        +obtener_mi_info()
        +health_check()
        +root()
        -get_current_user_id(): UUID
    }

    class CargaHorasService {
        +validar_horas_diarias(db: Session, recurso_id: UUID, fecha: date, nuevas_horas: Decimal, excluir_id: UUID): (bool, Decimal)
        +crear_carga_hora(db: Session, recurso_id: UUID, carga: CargaHoraCreate): dict
        +obtener_calendario_semanal(db: Session, recurso_id: UUID, fecha_referencia: date): dict
        +obtener_estadisticas_recurso(db: Session, recurso_id: UUID): dict
    }

    class ExternalApiClient {
        +get_proyectos_por_recurso(recurso_id: str): list
        +get_tareas_por_proyecto(proyecto_id: str): list
        +get_proyecto(proyecto_id: str): dict
        +get_tarea(tarea_id: str): dict
        +get_recurso(recurso_id: str): dict
    }

    class DatabaseSessionProvider {
        +get_db(): Session
    }

    class CargaHoraCreate {
        +tarea_id: UUID
        +proyecto_id: UUID
        +fecha: date
        +horas: Decimal
        +descripcion: str
        +validar_horas(v: Decimal): Decimal
    }

    class CargaHoraUpdate {
        +horas: Decimal
        +descripcion: str
        +validar_horas(v: Decimal): Decimal
    }

    class CargaHora {
        +id: UUID
        +recurso_id: UUID
        +tarea_id: UUID
        +proyecto_id: UUID
        +fecha: date
        +horas: Decimal
        +descripcion: str
        +created_at: datetime
    }

    class CargaHoraDetalle {
        +proyecto: dict
        +tarea: dict
        +recurso: dict
    }

    class EntradaProyecto {
        +carga_id: UUID
        +proyecto_id: UUID
        +proyecto_nombre: str
        +tarea_id: UUID
        +tarea_nombre: str
        +horas: Decimal
        +descripcion: str
    }

    class ResumenDiario {
        +fecha: date
        +dia_semana: str
        +total_horas: Decimal
        +entradas: List[EntradaProyecto]
    }

    class CalendarioSemanal {
        +recurso_id: UUID
        +recurso_nombre: str
        +fecha_inicio: date
        +fecha_fin: date
        +dias: List[ResumenDiario]
        +total_semana: Decimal
    }

    class EstadisticasRecurso {
        +recurso: dict
        +total_horas_mes_actual: Decimal
        +total_horas_semana_actual: Decimal
        +proyectos_activos: int
        +promedio_horas_diarias: Decimal
    }

    %% Relaciones
    HorasController --> CargaHorasService : usa
    HorasController --> ExternalApiClient : consulta datos externos
    HorasController --> DatabaseSessionProvider : inyección de Session
    HorasController --> AppConfig : CORS_ORIGINS / get_recurso_id_desarrollo

    CargaHorasService --> ExternalApiClient : valida proyecto/tarea/recurso
    CargaHorasService --> DatabaseSessionProvider : consultas SQL
    CargaHorasService --> CargaHoraCreate
    CargaHorasService --> CalendarioSemanal
    CargaHorasService --> EstadisticasRecurso

    CalendarioSemanal --> ResumenDiario
    ResumenDiario --> EntradaProyecto

    CargaHoraDetalle --> CargaHora
```

*Diagrama de código del módulo [Nombre del módulo] mostrando las clases principales y sus relaciones*

## Descripción de Clases

### Controladores
| Clase | Responsabilidades | Métodos Principales |
|-------|------------------|-------------------|
| [HorasController (módulo main.py)] | [Orquestar los endpoints HTTP de la API de carga de horas (FastAPI): proyectos, tareas, calendario, altas/bajas/modificaciones de horas, estadísticas, health check e información del usuario actual. Aplica validaciones de autorización por recurso (dueño de la carga).] | [obtener_mis_proyectos, obtener_tareas_proyecto, obtener_calendario, cargar_horas, actualizar_horas, eliminar_horas, obtener_estadisticas, obtener_mi_info, health_check, root] |

### Servicios
| Clase | Responsabilidades | Métodos Principales |
|-------|------------------|-------------------|
| [CargaHorasService (módulo services.py)] | [Encapsular la lógica de negocio de la carga de horas: validación de tope de 24 horas diarias, validación de existencia y relación proyecto–tarea–recurso contra APIs externas, inserción/consulta de datos en la tabla carga_horas, armado de calendario semanal y cálculo de estadísticas por recurso.] | [validar_horas_diarias, crear_carga_hora, obtener_calendario_semanal, obtener_estadisticas_recurso] |
| [AppConfig (módulo config.py)] | [Centralizar configuración de la aplicación: conexión a BD, IDs y URLs de APIs externas, parámetros de CORS, logging, puerto y timeout. Exponer el recurso_id de desarrollo.] | [get_recurso_id_desarrollo] |

### Repositorios
| Clase | Responsabilidades | Métodos Principales |
|-------|------------------|-------------------|
| [UserRepository] | [Acceso a datos] | [save, findById, findAll, deleteById] |

### Entidades
| Clase | Responsabilidades | Atributos Principales |
|-------|------------------|---------------------|
| [CargaHoraCreate] | [Modelo de entrada para creación de cargas de horas. Valida rangos de horas (0 < horas ≤ 24) y redondea a 2 decimales.] | [tarea_id, proyecto_id, fecha, horas, descripcion] |
| [CargaHoraUpdate] | [Modelo de entrada para actualización parcial de una carga (horas y/o descripción).] | [horas, descripcion] |
| [CargaHora] | [Modelo de respuesta base para una carga de horas persistida en BD.] | [id, recurso_id, tarea_id, proyecto_id, fecha, horas, descripcion, created_at] |
| [CargaHoraDetalle] | [Extiende CargaHora agregando información enriquecida de APIs externas (proyecto, tarea, recurso).] | [Hereda atributos de CargaHora + proyecto, tarea, recurso] |
| [EntradaProyecto] | [Representa una entrada de horas por proyecto/tarea dentro de un día del calendario.] | [carga_id, proyecto_id, proyecto_nombre, tarea_id, tarea_nombre, horas, descripcion] |
| [ResumenDiario] | [Agrega y agrupa las horas de un día: total diario y lista de entradas por proyecto/tarea.] | [fecha, dia_semana, total_horas, entradas] |
| [CalendarioSemanal] | [Modelo de respuesta para el calendario semanal completo de un recurso (lunes a domingo).] | [recurso_id, recurso_nombre, fecha_inicio, fecha_fin, dias, total_semana] |
| [EstadisticasRecurso] | [Modelo de respuesta para las estadísticas de un recurso (mes, semana, proyectos activos, promedio).] | [recurso, total_horas_mes_actual, total_horas_semana_actual, proyectos_activos, promedio_horas_diarias] |


## Patrones de Diseño Utilizados

### Capa de Servicio (Service Layer)
Toda la lógica de negocio relacionada con la carga de horas está centralizada en `CargaHorasService`.  
Los endpoints actúan como orquestadores y delegan validaciones y reglas de negocio al servicio.

### DTOs / Modelos de Validación con Pydantic
Los modelos de `models.py` (`CargaHoraCreate`, `CargaHoraUpdate`, `CalendarioSemanal`, etc.) se utilizan para validar y tipar entradas/salidas de la API, asegurando contratos claros entre frontend y backend.

### Inyección de dependencias (FastAPI)
El acceso a BD (`get_db`) y el usuario actual (`get_current_user_id`) se resuelven como dependencias, desacoplando la capa de presentación de los detalles de infraestructura.

### Cliente externo especializado
El acceso a las APIs externas se centraliza en `external_apis.api_client`, evitando que la capa de presentación y servicios tengan lógica duplicada de consumo HTTP.


## Notas Adicionales

[Información adicional sobre la estructura de código, convenciones de naming, o cualquier detalle relevante]

---

**Versión:** 1.0  
**Estado:** [Borrador/En revisión/Aprobado]
