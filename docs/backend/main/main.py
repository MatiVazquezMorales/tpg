from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from uuid import UUID

# --- IMPORTS CORREGIDOS ---
# Asegúrate de que tus carpetas se llamen así (models, db, services, external_apis)
from models import models as schemas
# Si tu archivo de base de datos está en la carpeta 'db', usa esto:
from db.database import get_db 
# Si está en 'database', cámbialo a: from database.database import get_db

from services.services import CargaHorasService
from external_apis.external_apis import api_client # Corregido para apuntar a api_client.py
from config.config import get_recurso_id_desarrollo, CORS_ORIGINS, PORT

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

# ==================== CONFIGURACIÓN ====================

def get_current_user_id() -> str:
    """Retorna el ID del recurso como string para compatibilidad"""
    return str(get_recurso_id_desarrollo())

# ==================== ENDPOINTS NUEVOS (FLUJO TAREA -> PROYECTO) ====================

@app.get("/api/tareas/me", 
         summary="Obtener todas las tareas del usuario actual")
def obtener_mis_tareas():
    """
    Retorna TODAS las tareas asignadas al usuario logueado.
    """
    recurso_id = get_current_user_id()
    try:
        return api_client.get_tareas_por_recurso(recurso_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error obteniendo tareas: {str(e)}"
        )

@app.get("/api/proyectos/{proyecto_id}",
         summary="Obtener detalle de un proyecto por ID")
def obtener_proyecto(proyecto_id: str):
    """
    Retorna el detalle (nombre, descripción) de un proyecto.
    """
    try:
        proyecto = api_client.get_proyecto(proyecto_id)
        if not proyecto:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return proyecto
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error obteniendo proyecto: {str(e)}"
        )

# ==================== ENDPOINTS GENERALES ====================

@app.get("/api/proyectos", summary="Obtener proyectos asignados")
def obtener_mis_proyectos():
    recurso_id = get_current_user_id()
    try:
        return api_client.get_proyectos_por_recurso(recurso_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error: {str(e)}")

@app.get("/api/proyectos/{proyecto_id}/tareas", summary="Obtener tareas de un proyecto")
def obtener_tareas_proyecto(proyecto_id: str):
    recurso_id = get_current_user_id()
    try:
        tareas_proyecto = api_client.get_tareas_por_proyecto(proyecto_id)
        # Filtrar por usuario
        return [t for t in tareas_proyecto if str(t.get('recursoId')) == recurso_id]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error: {str(e)}")

@app.get("/api/calendario",
         summary="Obtener calendario semanal",
         response_model=schemas.CalendarioSemanal)
def obtener_calendario(
    fecha: Optional[date] = Query(None, description="Fecha de referencia"),
    db: Session = Depends(get_db)
):
    recurso_id = get_current_user_id()
    if not fecha:
        fecha = date.today()
    
    # Nota: CargaHorasService espera UUID, pero al ser string la DB (VARCHAR),
    # el servicio debería manejarlo o castearlo.
    # Si CargaHorasService usa UUID(recurso_id), funcionará siempre que el string sea un UUID válido.
    # Si el ID es "raro" (el de la API Mock), el servicio podría fallar si intenta convertir a UUID estricto.
    # Asumimos que services.py maneja strings o que los IDs son compatibles.
    return CargaHorasService.obtener_calendario_semanal(db, recurso_id, fecha)

# ==================== ENDPOINTS CARGA DE HORAS (Lógica Restaurada) ====================

@app.post("/api/horas",
          status_code=status.HTTP_201_CREATED,
          summary="Cargar horas trabajadas")
def cargar_horas(
    carga: schemas.CargaHoraCreate,
    db: Session = Depends(get_db)
):
    recurso_id = get_current_user_id()
    # Restaurada la llamada al servicio
    resultado = CargaHorasService.crear_carga_hora(db, recurso_id, carga)
    return resultado

@app.put("/api/horas/{carga_id}",
         summary="Actualizar carga de horas")
def actualizar_horas(
    carga_id: str, # Cambiado a str
    carga: schemas.CargaHoraUpdate,
    db: Session = Depends(get_db)
):
    recurso_id = get_current_user_id()
    
    # Verificar pertenencia (Query SQL directa porque el ORM puede ser estricto con tipos)
    result = db.execute(
        text("SELECT recurso_id, fecha, horas FROM carga_horas WHERE id = :carga_id"),
        {"carga_id": carga_id} # Pasamos str directamente, la DB es VARCHAR o UUID (compatible si es válido)
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Carga no encontrada")
    
    if str(row[0]) != recurso_id:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    
    # Validar horas
    if carga.horas is not None:
        es_valido, total = CargaHorasService.validar_horas_diarias(
            db, recurso_id, row[1], carga.horas, carga_id
        )
        if not es_valido:
            raise HTTPException(status_code=400, detail=f"Excede 24hs diarias. Actual: {total}")
    
    # Update dinámico
    updates = []
    params = {"carga_id": carga_id}
    
    if carga.horas is not None:
        updates.append("horas = :horas")
        params["horas"] = float(carga.horas)
    
    if carga.descripcion is not None:
        updates.append("descripcion = :descripcion")
        params["descripcion"] = carga.descripcion
        
    if not updates:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
        
    query = text(f"UPDATE carga_horas SET {', '.join(updates)} WHERE id = :carga_id RETURNING id, horas, descripcion")
    result = db.execute(query, params)
    row = result.fetchone()
    db.commit()
    
    return {"id": str(row[0]), "horas": float(row[1]), "descripcion": row[2]}

@app.delete("/api/horas/{carga_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Eliminar carga de horas")
def eliminar_horas(carga_id: str, db: Session = Depends(get_db)): # Cambiado a str
    recurso_id = get_current_user_id()
    
    result = db.execute(
        text("SELECT recurso_id FROM carga_horas WHERE id = :carga_id"),
        {"carga_id": carga_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Carga no encontrada")
    
    if str(row[0]) != recurso_id:
        raise HTTPException(status_code=403, detail="No tienes permiso")
        
    db.execute(text("DELETE FROM carga_horas WHERE id = :carga_id"), {"carga_id": carga_id})
    db.commit()
    return None

# ==================== OTROS ENDPOINTS ====================

@app.get("/api/estadisticas", response_model=schemas.EstadisticasRecurso)
def obtener_estadisticas(db: Session = Depends(get_db)):
    recurso_id = get_current_user_id()
    return CargaHorasService.obtener_estadisticas_recurso(db, recurso_id)

@app.get("/api/recursos/me", summary="Info usuario")
def obtener_mi_info():
    recurso_id = get_current_user_id()
    try:
        recurso = api_client.get_recurso(recurso_id)
        if not recurso:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        rol_nombre = "Empleado"
        if 'rolId' in recurso:
            rol_info = api_client.get_rol(recurso['rolId'])
            if rol_info and 'nombre' in rol_info:
                exp = rol_info.get('experiencia', '')
                rol_nombre = f"{rol_info['nombre']} {exp}".strip()
        
        recurso['rol_nombre'] = rol_nombre
        return recurso
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=503, detail="Error al obtener info usuario")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Sistema de Carga de Horas PSA"}

@app.get("/")
def root():
    return {"service": "Sistema de Carga de Horas PSA", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)