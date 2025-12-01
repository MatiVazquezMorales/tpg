# Guía Rápida: Deploy en Render

## Pasos Rápidos

### 1. Preparar el Repositorio
- El repositorio ya tiene `render.yaml` configurado
- El `Dockerfile` está listo para producción
- La base de datos se inicializa automáticamente

### 2. Crear Servicios en Render

#### Usando Blueprint 
1. Ir a [render.com](https://render.com) 
2. En el dashboard, clic en **"New +"** → **"Blueprint"**
3. Conectar repositorio de GitHub/GitLab
4. Render detectará automáticamente el `render.yaml`
5. Revisar y ajustar las variables de entorno:
   - `CORS_ORIGINS`: URL de frontend
   - `FINANZAS_API_URL`: URL del módulo de finanzas
   - `USE_FINANZAS_MOCK`: `"false"` para producción

**Variables de Entorno:**
   ```
   DATABASE_URL=<Internal Database URL de la BD que creaste>
   PORT=8000
   CORS_ORIGINS=https://tu-frontend.onrender.com
   USE_FINANZAS_MOCK=false
   FINANZAS_API_URL=https://modulo-finanzas.onrender.com/api/finanzas/calcular-costos
   API_TIMEOUT=30
   LOG_LEVEL=info
   ```

**Health Check Path**: `/health`

### Verificar el Deploy

Una vez desplegado, verificar:

```bash
# Health check
curl https://tu-backend.onrender.com/health

# Debería responder: {"status": "ok", "service": "Sistema de Carga de Horas PSA"}

# Documentación
# Visitar: https://tu-backend.onrender.com/docs
```

### 4. Integración con Frontend y Módulo de Finanzas

- **Frontend**: Configurar la URL del backend en las llamadas API
- **Módulo de Finanzas**: 
  - El backend expone: `GET /api/horas-aprobadas`
  - El backend consume: `POST /api/finanzas/calcular-costos` (configurado en `FINANZAS_API_URL`)

## Notas Importantes

- ✅ La base de datos se inicializa automáticamente al arrancar el backend
- ✅ El backend está configurado para producción (sin `--reload`)
- ✅ CORS está configurado para permitir el frontend
- ⚠️  En el plan gratuito, Render "duerme" los servicios después de 15 minutos de inactividad
- ⚠️  La primera petición después de dormir puede tardar ~30 segundos

## Troubleshooting

### El backend no arranca
- Verificar los logs en el dashboard de Render
- Asegúrar de que `DATABASE_URL` esté configurado correctamente
- Verificar que el `Dockerfile` esté en la raíz del proyecto

### Error de conexión a la base de datos
- Verificar que la base de datos esté creada y activa
- Usa la **Internal Database URL** (no la externa) para servicios en la misma cuenta de Render
- Verificar que el servicio de backend esté vinculado a la base de datos

### CORS errors desde el frontend
- Verificar que `CORS_ORIGINS` incluya la URL exacta de frontend
- Asegurar de que no haya espacios extra en la variable de entorno

