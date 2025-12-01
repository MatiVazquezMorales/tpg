# Guía de Deployment - Sistema de Carga de Horas

## Deployment en Render

### Método Recomendado: Usando render.yaml

Este proyecto incluye un archivo `render.yaml` que configura automáticamente el servicio y la base de datos en Render.

#### Pasos para desplegar:

1. **Crear cuenta en Render** (si no tienes una)
   - Ve a [render.com](https://render.com)
   - Crea una cuenta gratuita (suficiente para trabajo académico)

2. **Conectar el repositorio**
   - En el dashboard de Render, haz clic en "New +"
   - Selecciona "Blueprint" (si usas `render.yaml`) o "Web Service" (si prefieres configuración manual)
   - Conecta tu repositorio de GitHub/GitLab

3. **Si usas Blueprint (render.yaml):**
   - Render detectará automáticamente el archivo `render.yaml`
   - Revisa y ajusta las variables de entorno según necesites:
     - `CORS_ORIGINS`: URL de tu frontend (ej: `https://tu-frontend.onrender.com`)
     - `FINANZAS_API_URL`: URL del módulo de finanzas en Render
     - `USE_FINANZAS_MOCK`: `"false"` para producción, `"true"` para pruebas

4. **Si prefieres configuración manual:**
   - Tipo: **Web Service**
   - Runtime: **Docker**
   - Dockerfile Path: `./Dockerfile`
   - Docker Context: `.` (raíz del proyecto)
   - Plan: **Free** (suficiente para trabajo académico)

5. **Crear Base de Datos PostgreSQL:**
   - En Render, crea un nuevo **PostgreSQL** database
   - Plan: **Free**
   - Render proporcionará automáticamente la variable `DATABASE_URL`
   - **Importante**: El script `init.sql` se ejecutará automáticamente la primera vez que el backend se conecte

6. **Configurar Variables de Entorno:**
   ```
   DATABASE_URL=<Render lo proporciona automáticamente si vinculaste la BD>
   PORT=8000
   CORS_ORIGINS=https://tu-frontend.onrender.com,http://localhost:8080
   USE_FINANZAS_MOCK=false
   FINANZAS_API_URL=https://modulo-finanzas.onrender.com/api/finanzas/calcular-costos
   API_TIMEOUT=30
   LOG_LEVEL=info
   ```

7. **Health Check:**
   - Render usará automáticamente `/health` si está configurado en `render.yaml`
   - O configúralo manualmente en el dashboard: Path: `/health`

### Configuración de la Base de Datos

El script `docs/backend/db/init.sql` se ejecutará **automáticamente** cuando el backend arranque gracias al script `init_db.py` que se ejecuta en el evento de startup de FastAPI.

**Nota**: Si necesitas ejecutarlo manualmente por alguna razón:

1. Obtén las credenciales de la base de datos desde el dashboard de Render
2. Conéctate usando un cliente PostgreSQL o desde la terminal:
   ```bash
   psql $DATABASE_URL < docs/backend/db/init.sql
   ```

### Verificación Post-Deployment

Una vez desplegado, verifica que todo funcione:

1. **Health Check**: 
   ```bash
   curl https://tu-backend.onrender.com/health
   ```
   Debería responder: `{"status": "ok", "service": "Sistema de Carga de Horas PSA"}`

2. **Documentación de la API**:
   - Visita: `https://tu-backend.onrender.com/docs`
   - O la versión alternativa: `https://tu-backend.onrender.com/redoc`

3. **Endpoint de horas aprobadas** (para el módulo de finanzas):
   ```bash
   curl https://tu-backend.onrender.com/api/horas-aprobadas
   ```

### Integración con Módulo de Finanzas

#### Si ambos están en la misma red Docker:

En `docker-compose.yml` o variables de entorno:
```yaml
FINANZAS_API_URL: "http://servidor-finanzas:8001/api/finanzas/calcular-costos"
USE_FINANZAS_MOCK: "false"
```

#### Si están en servicios separados:

Usar la URL pública o interna del servicio de finanzas:
```yaml
FINANZAS_API_URL: "https://tu-modulo-finanzas.onrender.com/api/finanzas/calcular-costos"
USE_FINANZAS_MOCK: "false"
```

### Endpoint que expone este módulo para Finanzas

**GET** `/api/horas-aprobadas`

Formato de respuesta:
```json
[
  {
    "tareaId": "uuid",
    "recursoId": "uuid",
    "periodos": [
      { "anio": 2025, "mes": 11, "horas_aprobadas": 8.0 }
    ]
  }
]
```

### Checklist de Deployment

- [ ] Dockerfile configurado (sin `--reload` para producción)
- [ ] Variables de entorno configuradas en el servicio
- [ ] `USE_FINANZAS_MOCK=false` si se usa el módulo real
- [ ] `FINANZAS_API_URL` apuntando al servicio correcto
- [ ] Base de datos configurada (PostgreSQL)
- [ ] CORS configurado si el frontend está en otro dominio
- [ ] Health check configurado: `GET /health`

### Notas Importantes

- El Dockerfile está configurado para producción (sin `--reload`)
- Para desarrollo local, descomentar el `command` en `docker-compose.yml`
- El mock de finanzas está activado por defecto (`USE_FINANZAS_MOCK=true`)
- La base de datos se inicializa automáticamente con `init.sql` al crear el contenedor

