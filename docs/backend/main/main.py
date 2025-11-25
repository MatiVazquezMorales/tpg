from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import date, timedelta
from uuid import UUID

import models as schemas
from database import get_db
from services import CargaHorasService
from external_apis import api_client
from config import get_recurso_id_desarrollo, CORS_ORIGINS

app = FastAPI(
    title="Sistema de Carga de Horas PSA",
    description="API para gestión de carga de horas de proyectos",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CONFIGURACIÓN DE DESARROLLO ====================

def get_current_user_id() -> UUID:
    """
    Retorna el ID del recurso hardcodeado para desarrollo.
    Configurado en config.py
    """
    return get_recurso_id_desarrollo()

# ==================== ENDPOINTS: CARGA DE HORAS ====================

@app.get("/api/proyectos", 
         summary="Obtener proyectos asignados al usuario actual")
def obtener_mis_proyectos():
    """
    Retorna los proyectos donde el usuario tiene tareas asignadas.
    Esto se determina a partir de las tareas en la API externa.
    """
    recurso_id = get_current_user_id()
    
    try:
        proyectos = api_client.get_proyectos_por_recurso(str(recurso_id))
        return proyectos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al obtener proyectos: {str(e)}"
        )

@app.get("/api/proyectos/{proyecto_id}/tareas",
         summary="Obtener tareas de un proyecto")
def obtener_tareas_proyecto(proyecto_id: UUID):
    """
    Retorna las tareas disponibles para un proyecto específico.
    Idealmente solo deberían verse las tareas asignadas al usuario.
    """
    recurso_id = get_current_user_id()
    
    try:
        # Obtener todas las tareas del proyecto
        tareas_proyecto = api_client.get_tareas_por_proyecto(str(proyecto_id))
        
        # Filtrar solo las tareas asignadas al usuario actual
        tareas_usuario = [
            t for t in tareas_proyecto 
            if t.get('recursoId') == str(recurso_id)
        ]
        
        return tareas_usuario
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al obtener tareas: {str(e)}"
        )

@app.get("/api/calendario",
         summary="Obtener calendario semanal",
         response_model=schemas.CalendarioSemanal)
def obtener_calendario(
    fecha: Optional[date] = Query(
        None, 
        description="Fecha de referencia (se ajusta al lunes de esa semana). Si no se provee, usa la semana actual"
    ),
    db: Session = Depends(get_db)
):
    """
    Retorna el calendario semanal del usuario con todas sus cargas de horas.
    La semana va de lunes a domingo.
    """
    recurso_id = get_current_user_id()
    
    if not fecha:
        fecha = date.today()
    
    calendario = CargaHorasService.obtener_calendario_semanal(
        db, recurso_id, fecha
    )
    
    return calendario

@app.post("/api/horas",
          status_code=status.HTTP_201_CREATED,
          summary="Cargar horas trabajadas")
def cargar_horas(
    carga: schemas.CargaHoraCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva carga de horas para el usuario actual.
    
    Validaciones:
    - Proyecto y tarea deben existir
    - Tarea debe pertenecer al proyecto
    - No se pueden cargar más de 24 horas en un día
    - Las horas deben ser mayores a 0
    """
    recurso_id = get_current_user_id()
    
    resultado = CargaHorasService.crear_carga_hora(
        db, recurso_id, carga
    )
    
    return resultado

@app.put("/api/horas/{carga_id}",
         summary="Actualizar carga de horas")
def actualizar_horas(
    carga_id: UUID,
    carga: schemas.CargaHoraUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una carga de horas existente.
    Solo se pueden actualizar las horas y/o la descripción.
    """
    recurso_id = get_current_user_id()
    
    # Verificar que la carga pertenece al usuario
    result = db.execute(
        text("""
            SELECT recurso_id, fecha, horas 
            FROM carga_horas 
            WHERE id = :carga_id
        """),
        {"carga_id": str(carga_id)}
    )
    
    row = result.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carga de horas no encontrada"
        )
    
    if str(row[0]) != str(recurso_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar esta carga"
        )
    
    # Validar horas si se están actualizando
    if carga.horas is not None:
        es_valido, total_actual = CargaHorasService.validar_horas_diarias(
            db, recurso_id, row[1], carga.horas, carga_id
        )
        
        if not es_valido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pueden cargar más de 24 horas en un día. "
                       f"Total actual (sin esta carga): {total_actual} horas"
            )
    
    # Construir actualización dinámica
    updates = []
    params = {"carga_id": str(carga_id)}
    
    if carga.horas is not None:
        updates.append("horas = :horas")
        params["horas"] = float(carga.horas)
    
    if carga.descripcion is not None:
        updates.append("descripcion = :descripcion")
        params["descripcion"] = carga.descripcion
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay campos para actualizar"
        )
    
    query = text(f"""
        UPDATE carga_horas
        SET {', '.join(updates)}
        WHERE id = :carga_id
        RETURNING id, horas, descripcion
    """)
    
    result = db.execute(query, params)
    row = result.fetchone()
    db.commit()
    
    return {
        "id": str(row[0]),
        "horas": float(row[1]),
        "descripcion": row[2]
    }

@app.delete("/api/horas/{carga_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Eliminar carga de horas")
def eliminar_horas(carga_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina una carga de horas.
    Solo el dueño de la carga puede eliminarla.
    """
    recurso_id = get_current_user_id()
    
    # Verificar pertenencia
    result = db.execute(
        text("SELECT recurso_id FROM carga_horas WHERE id = :carga_id"),
        {"carga_id": str(carga_id)}
    )
    
    row = result.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carga de horas no encontrada"
        )
    
    if str(row[0]) != str(recurso_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta carga"
        )
    
    db.execute(
        text("DELETE FROM carga_horas WHERE id = :carga_id"),
        {"carga_id": str(carga_id)}
    )
    db.commit()
    
    return None

@app.get("/api/estadisticas",
         summary="Obtener estadísticas del usuario",
         response_model=schemas.EstadisticasRecurso)
def obtener_estadisticas(db: Session = Depends(get_db)):
    """
    Retorna estadísticas generales del usuario:
    - Total de horas del mes actual
    - Total de horas de la semana actual
    - Cantidad de proyectos activos
    - Promedio de horas diarias
    """
    recurso_id = get_current_user_id()
    
    estadisticas = CargaHorasService.obtener_estadisticas_recurso(
        db, recurso_id
    )
    
    return estadisticas

# ==================== ENDPOINTS: INFORMACIÓN (PROXY) ====================

@app.get("/api/recursos/me",
         summary="Obtener información del usuario actual")
def obtener_mi_info():
    """Retorna la información del usuario de desarrollo"""
    recurso_id = get_current_user_id()
    
    try:
        recurso = api_client.get_recurso(str(recurso_id))
        if not recurso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Información del usuario no encontrada"
            )
        return recurso
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al obtener información del usuario: {str(e)}"
        )

# ==================== HEALTH CHECK ====================

@app.get("/health")
def health_check():
    """Endpoint para verificar que el servicio está funcionando"""
    return {
        "status": "ok",
        "service": "Sistema de Carga de Horas PSA"
    }

@app.get("/")
def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "Sistema de Carga de Horas PSA",
        "version": "1.0.0",
        "description": "Módulo de carga de horas de proyectos",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    from config import PORT
    uvicorn.run(app, host="0.0.0.0", port=PORT)