# Guía de Configuración - Sistema de Carga de Horas

## Requisitos Previos

- Docker y Docker Compose instalados
- Git (para clonar el repositorio)

## Inicio Rápido con Docker

### 1. Levantar los servicios

```bash
docker compose up -d
```

Esto iniciará:
- **Backend** (FastAPI): `http://localhost:8000`
- **Base de datos** (PostgreSQL): Puerto `5433`
- **Nginx** (Frontend): `http://localhost:8080`

### 2. Verificar que todo esté funcionando

```bash
# Ver estado de los contenedores
docker compose ps

# Ver logs
docker compose logs -f
```

### 3. Acceder a la aplicación

- **Frontend**: `http://localhost:8080`
- **Backend API**: `http://localhost:8000`
- **Documentación API**: `http://localhost:8000/docs`

## ⚠️ Configuración del Módulo de Finanzas (IMPORTANTE)

### Mock de Finanzas (Por Defecto)

El sistema viene configurado con un **mock del módulo de finanzas** activado por defecto. Esto permite probar la funcionalidad sin necesidad de tener el módulo de finanzas corriendo.

**Configuración actual:**
- `USE_FINANZAS_MOCK=true` (por defecto)
- El mock genera costos en USD basados en roles y períodos
- Valores de ejemplo: $35-75 USD/hora según el rol

### Usar el Módulo de Finanzas Real

Si se quiere conectar con el módulo de finanzas real:

1. **Configurar la URL del módulo de finanzas** en `docker-compose.yml`:
```yaml
environment:
  FINANZAS_API_URL: "http://servidor-finanzas:puerto/api/finanzas/calcular-costos"
  USE_FINANZAS_MOCK: "false"
```

2. **Reconstruir y reiniciar**:
```bash
docker compose down
docker compose up -d --build
```

### Endpoint de Horas Aprobadas

El módulo de finanzas consume el endpoint:
- **GET** `/api/horas-aprobadas`
- **Formato**: Array de objetos con `tareaId`, `recursoId` y `periodos` (año, mes, horas_aprobadas)

## Comandos Útiles

```bash
# Detener los servicios
docker compose down

# Detener y eliminar volúmenes (elimina la base de datos)
docker compose down -v

# Reconstruir las imágenes
docker compose build

# Ver logs del backend
docker compose logs backend -f

# Ver logs de la base de datos
docker compose logs db -f
```

## Estructura del Proyecto

```
├── docs/
│   ├── backend/          # Backend FastAPI
│   │   ├── main/         # Endpoints de la API
│   │   ├── services/     # Lógica de negocio
│   │   ├── db/           # Scripts de base de datos
│   │   └── config/       # Configuración (incluye mock de finanzas)
│   └── frontend/         # Frontend HTML/CSS/JS
├── docker-compose.yml    # Configuración de servicios
├── Dockerfile           # Imagen del backend
└── requirements.txt     # Dependencias Python
```

## Notas Importantes

- **Límite de horas**: Se pueden cargar hasta **24 horas por día** (permite guardias)
- **Campo de notas**: Es opcional pero recomendado
- **Selección de tareas**: Primero se selecciona un proyecto, luego las tareas de ese proyecto
- **Base de datos**: Se inicializa automáticamente al levantar Docker por primera vez
- **APIs externas**: Son mocks de Mulesoft (recursos, proyectos, tareas)

## Solución de Problemas

### El backend no inicia
- Verificar logs: `docker compose logs backend`
- Verificar que el puerto 8000 no esté en uso
- Reconstruir: `docker compose build backend`

### Error de conexión a la base de datos
- Verificar que el contenedor `db` esté corriendo: `docker compose ps`
- Verificar logs: `docker compose logs db`

### El mock de finanzas no funciona
- Verificar que `USE_FINANZAS_MOCK=true` en la configuración
- Ver logs del backend para ver errores: `docker compose logs backend | grep -i mock`
