from fastapi import FastAPI, Depends, HTTPException, status, Query, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from uuid import UUID
import httpx

from models import models as schemas
from db.database import get_db 
from services.services import CargaHorasService
from external_apis.external_apis import api_client
from config.config import get_recurso_id_desarrollo, CORS_ORIGINS, PORT, USE_FINANZAS_MOCK, FINANZAS_API_BASE_URL, FINANZAS_TARIFAS_URL

app = FastAPI(
    title="Sistema de Carga de Horas PSA",
    description="API para gestión de carga de horas de proyectos",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al arrancar la aplicación"""
    try:
        from db.init_db import init_database
        init_database()
    except Exception as e:
        print(f"⚠️  No se pudo inicializar la base de datos automáticamente: {e}")
        print("   La aplicación continuará, pero asegúrate de que el esquema esté creado")

# Configurar CORS - Permitir cualquier origen (proyecto académico)
# Para producción, configurar CORS_ORIGINS con orígenes específicos
if CORS_ORIGINS == "*":
    # Permitir todos los orígenes (sin credenciales - requerido cuando se usa "*")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Orígenes específicos (puede usar credenciales si es necesario)
    origins_list = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def get_current_user_id() -> str:
    """Retorna el ID del recurso como string para compatibilidad"""
    return str(get_recurso_id_desarrollo())


@app.get("/api/tareas/me", 
         summary="Obtener todas las tareas del usuario actual")
def obtener_mis_tareas():

    recurso_id = get_current_user_id()
    try:
        return api_client.get_tareas_por_recurso(recurso_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error obteniendo tareas: {str(e)}"
        )

@app.get("/api/proyectos/all", summary="Obtener todos los proyectos")
def obtener_todos_los_proyectos(db: Session = Depends(get_db)):
    """Endpoint para gerentes: obtiene todos los proyectos disponibles con estadísticas"""
    try:
        proyectos = api_client.get_todos_los_proyectos()
        
        # Enriquecer cada proyecto con estadísticas
        proyectos_enriquecidos = []
        for proyecto in proyectos:
            proyecto_copy = proyecto.copy()
            proyecto_id = proyecto.get('id')
            
            if proyecto_id:
                # Obtener horas totales del proyecto
                horas_totales = CargaHorasService.obtener_horas_totales_proyecto(db, proyecto_id)
                proyecto_copy['horas_totales'] = horas_totales
                
                # Contar tareas abiertas
                tareas_abiertas = api_client.contar_tareas_abiertas_proyecto(proyecto_id)
                proyecto_copy['tareas_abiertas'] = tareas_abiertas
            else:
                proyecto_copy['horas_totales'] = 0.0
                proyecto_copy['tareas_abiertas'] = 0
            
            proyectos_enriquecidos.append(proyecto_copy)
        
        return proyectos_enriquecidos
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error obteniendo proyectos: {str(e)}")

@app.get("/api/proyectos", summary="Obtener proyectos asignados")
def obtener_mis_proyectos():
    recurso_id = get_current_user_id()
    try:
        return api_client.get_proyectos_por_recurso(recurso_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error: {str(e)}")

@app.get("/api/proyectos/{proyecto_id}",
         summary="Obtener detalle de un proyecto por ID")
def obtener_proyecto(proyecto_id: str):

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

@app.get("/api/proyectos/{proyecto_id}/tareas", summary="Obtener tareas de un proyecto")
def obtener_tareas_proyecto(proyecto_id: str):
    recurso_id = get_current_user_id()
    try:
        tareas_proyecto = api_client.get_tareas_por_proyecto(proyecto_id)
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
    
    return CargaHorasService.obtener_calendario_semanal(db, recurso_id, fecha)

@app.post("/api/horas",
          status_code=status.HTTP_201_CREATED,
          summary="Cargar horas trabajadas")
def cargar_horas(
    carga: schemas.CargaHoraCreate,
    db: Session = Depends(get_db)
):
    recurso_id = get_current_user_id()
    resultado = CargaHorasService.crear_carga_hora(db, recurso_id, carga)
    return resultado

@app.put("/api/horas/{carga_id}",
         summary="Actualizar carga de horas")
def actualizar_horas(
    carga_id: str,
    carga: schemas.CargaHoraUpdate,
    db: Session = Depends(get_db)
):
    recurso_id = get_current_user_id()
    
    result = db.execute(
        text("SELECT recurso_id, fecha, horas FROM carga_horas WHERE id = :carga_id"),
        {"carga_id": carga_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Carga no encontrada")
    
    if str(row[0]) != recurso_id:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    
    if carga.horas is not None:
        es_valido, total = CargaHorasService.validar_horas_diarias(
            db, recurso_id, row[1], carga.horas, carga_id
        )
        if not es_valido:
            raise HTTPException(status_code=400, detail=f"Excede 24hs diarias. Actual: {total}")
    
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
def eliminar_horas(carga_id: str, db: Session = Depends(get_db)):
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

@app.get("/api/recursos", summary="Obtener todos los recursos/empleados")
def obtener_todos_los_recursos():
    """Endpoint para gerentes: obtiene todos los recursos con información de roles"""
    try:
        recursos = api_client.get_todos_los_recursos()
        return recursos
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error obteniendo recursos: {str(e)}")

@app.get("/api/recursos/{recurso_id}/calendario",
         summary="Obtener calendario semanal de un recurso específico",
         response_model=schemas.CalendarioSemanal)
def obtener_calendario_recurso(
    recurso_id: str,
    fecha: Optional[date] = Query(None, description="Fecha de referencia"),
    db: Session = Depends(get_db)
):
    """Endpoint para gerentes: obtiene el calendario semanal de un recurso específico"""
    if not fecha:
        fecha = date.today()
    
    return CargaHorasService.obtener_calendario_semanal(db, recurso_id, fecha)

@app.get("/api/recursos/{recurso_id}/tareas",
         summary="Obtener tareas de un recurso específico")
def obtener_tareas_recurso(recurso_id: str):
    """Endpoint para gerentes: obtiene las tareas asignadas a un recurso específico"""
    try:
        return api_client.get_tareas_por_recurso(recurso_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error obteniendo tareas: {str(e)}"
        )

@app.post("/api/recursos/{recurso_id}/horas",
          status_code=status.HTTP_201_CREATED,
          summary="Cargar horas trabajadas para un recurso específico")
def cargar_horas_recurso(
    recurso_id: str,
    carga: schemas.CargaHoraCreate,
    db: Session = Depends(get_db)
):
    """Endpoint para gerentes: carga horas trabajadas para un recurso específico"""
    resultado = CargaHorasService.crear_carga_hora(db, recurso_id, carga)
    return resultado

# Endpoint para el módulo de finanzas. Devuelve las horas aprobadas agrupadas por tarea, recurso y período (año/mes)    
@app.get("/api/horas-aprobadas",
         summary="Obtener horas aprobadas agrupadas por tarea, recurso y período",
         description="Endpoint para el módulo de finanzas. Devuelve las horas aprobadas agrupadas por tarea, recurso y período (año/mes)")
def obtener_horas_aprobadas(db: Session = Depends(get_db)):
    """Devuelve las horas aprobadas en formato requerido por el módulo de finanzas"""
    try:
        return CargaHorasService.obtener_horas_aprobadas_por_periodo(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo horas aprobadas: {str(e)}"
        )

def mock_finanzas_calcular_costos(horas_aprobadas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Mock del módulo de finanzas que genera costos por hora basados en roles.
    Genera costos de prueba para cada rolId y período encontrado en las horas aprobadas.
    """
    # Recopilar todos los períodos únicos de las horas aprobadas (fuera del try para que esté disponible)
    periodos_unicos = set()
    for horas in horas_aprobadas:
        for periodo in horas.get('periodos', []):
            periodos_unicos.add((periodo['anio'], periodo['mes']))
    
    # Costos base por rol en USD (valores realistas para diferentes niveles)
    costos_base_por_rol = {
        # Valores típicos por hora en USD según nivel de experiencia
        "f635b4ca-c091-472c-8b5a-cb3086d1973": 75.0,   # Senior Developer
        "d635b4ca-c091-472c-8b5a-cb3086d1978": 55.0,   # Semi-Senior Developer
        "1f14a491-e26d-4092-86ea-d76f20c165d1": 45.0,  # Mid-Level Developer
        "2e6ecd47-fa18-490e-b25a-c9101a398b6d": 35.0,  # Junior Developer
    }
    
    # Si no hay costos base definidos, usar valor por defecto (Mid-Level)
    costo_base_default = 50.0
    
    # Intentar obtener recursos para mapear recursoId -> rolId
    roles_unicos = set()
    try:
        recursos = api_client.get_todos_los_recursos()
        recursos_map = {r['id']: r.get('rolId') for r in recursos if 'id' in r and 'rolId' in r}
        
        # Recopilar roles únicos de las horas aprobadas
        for horas in horas_aprobadas:
            recurso_id = horas.get('recursoId')
            rol_id = recursos_map.get(recurso_id)
            
            if rol_id:
                roles_unicos.add(rol_id)
    except Exception as e:
        # Si hay error obteniendo recursos, usar valores por defecto
        print(f"⚠️  Error en mock de finanzas obteniendo recursos: {e}")
        # Continuar sin mapeo de recursos
    
    # Si no hay roles únicos, usar un rol mock por defecto
    if not roles_unicos:
        roles_unicos.add("f635b4ca-c091-472c-8b5a-cb3086d1973")
    
    # Generar respuesta en el formato esperado
    resultado = []
    
    for rol_id in roles_unicos:
        costo_base = costos_base_por_rol.get(rol_id, costo_base_default)
        periodos_rol = []
        
        # Ordenar períodos por año y mes
        periodos_ordenados = sorted(periodos_unicos, key=lambda x: (x[0], x[1]))
        
        for anio, mes in periodos_ordenados:
            # Simular variación de costos entre meses (ajustes menores, más realista)
            variacion = 1.0 + (mes % 3) * 0.02  # Variación del 0% al 4% (más realista)
            costo_hora = costo_base * variacion
            
            periodos_rol.append({
                "anio": anio,
                "mes": mes,
                "costo_hora": round(costo_hora, 2)
            })
        
        if periodos_rol:
            resultado.append({
                "rolId": rol_id,
                "periodos": periodos_rol
            })
    
    return resultado

async def obtener_tarifas_finanzas(horas_aprobadas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Obtiene las tarifas del módulo de finanzas usando GET /api/tarifas
    y las transforma al formato esperado por el frontend.
    """
    # Recopilar años únicos de las horas aprobadas
    años_unicos = set()
    for horas in horas_aprobadas:
        for periodo in horas.get('periodos', []):
            años_unicos.add(periodo['anio'])
    
    # Obtener tarifas para cada año
    tarifas_por_año = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        for año in años_unicos:
            try:
                url = f"{FINANZAS_TARIFAS_URL}?anio={año}"
                print(f"📡 Obteniendo tarifas del año {año} desde: {url}")
                response = await client.get(url)
                
                if response.status_code == 200:
                    tarifas_data = response.json()
                    tarifas_por_año[año] = tarifas_data
                    print(f"✅ Tarifas obtenidas para año {año}: {len(tarifas_data.get('roles', []))} roles")
                else:
                    print(f"⚠️  Error obteniendo tarifas para año {año}: Status {response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error obteniendo tarifas del módulo de finanzas para año {año}: {response.text[:500]}"
                    )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Error de conexión con el módulo de finanzas: {str(e)}"
                )
    
    # Obtener recursos para mapear recursoId -> rolId
    recursos_map = {}
    try:
        recursos = api_client.get_todos_los_recursos()
        recursos_map = {r['id']: r.get('rolId') for r in recursos if 'id' in r and 'rolId' in r}
    except Exception as e:
        print(f"⚠️  Error obteniendo recursos para mapeo: {e}")
    
    # Transformar tarifas al formato esperado
    resultado = []
    roles_procesados = set()
    
    # Recopilar roles únicos de las horas aprobadas
    for horas in horas_aprobadas:
        recurso_id = horas.get('recursoId')
        rol_id = recursos_map.get(recurso_id)
        
        if rol_id and rol_id not in roles_procesados:
            roles_procesados.add(rol_id)
            
            # Buscar tarifa para este rol en cada año
            periodos_rol = []
            for año in sorted(años_unicos):
                if año in tarifas_por_año:
                    tarifas_año = tarifas_por_año[año]
                    rol_tarifa = next((r for r in tarifas_año.get('roles', []) if r.get('id') == rol_id), None)
                    
                    if rol_tarifa:
                        # El formato de "valores" es un objeto donde las claves son strings de meses (ej: "7", "8", "9")
                        # y los valores son los costos por hora para ese mes
                        valores = rol_tarifa.get('valores', {})
                        
                        # Recopilar meses únicos de las horas aprobadas para este año
                        meses_necesarios = set()
                        for horas in horas_aprobadas:
                            for periodo in horas.get('periodos', []):
                                if periodo['anio'] == año:
                                    meses_necesarios.add(periodo['mes'])
                        
                        # Si no hay meses específicos, usar todos los meses (1-12)
                        if not meses_necesarios:
                            meses_necesarios = set(range(1, 13))
                        
                        # Agregar períodos para cada mes necesario
                        for mes in sorted(meses_necesarios):
                            # Buscar el costo para este mes específico en "valores"
                            # Las claves pueden ser strings ("7") o números (7)
                            mes_str = str(mes)
                            costo_hora = None
                            
                            if isinstance(valores, dict):
                                # Intentar obtener el costo para este mes
                                if mes_str in valores:
                                    costo_hora = float(valores[mes_str])
                                elif mes in valores:
                                    costo_hora = float(valores[mes])
                                else:
                                    # Si no hay costo específico para este mes, usar el primer valor disponible
                                    # o un valor por defecto
                                    for key, value in valores.items():
                                        if isinstance(value, (int, float)) and value > 0:
                                            costo_hora = float(value)
                                            break
                            
                            # Si no encontramos costo, usar valor por defecto
                            if costo_hora is None:
                                costo_hora = 50.0  # Valor por defecto
                                print(f"⚠️  No se encontró costo para rol {rol_id} en año {año} mes {mes}, usando valor por defecto: {costo_hora}")
                            
                            periodos_rol.append({
                                "anio": año,
                                "mes": mes,
                                "costo_hora": round(costo_hora, 2)
                            })
            
            if periodos_rol:
                resultado.append({
                    "rolId": rol_id,
                    "periodos": periodos_rol
                })
    
    return resultado

@app.post("/api/costos/calcular",
         summary="Calcular costos basados en horas aprobadas",
         description="Endpoint que actúa como proxy hacia el módulo de finanzas para calcular costos")
async def calcular_costos(request: Request):
    """
    Calcula los costos enviando las horas aprobadas al módulo de finanzas.
    Si USE_FINANZAS_MOCK está activado, usa datos mock. Si no, llama a la API real.
    """
    try:
        # Obtener el body como JSON
        body = await request.json()
        
        # Log para debugging (solo en desarrollo)
        print(f"📥 Request recibido en /api/costos/calcular")
        print(f"📦 Tipo de body: {type(body)}")
        print(f"📦 Contenido (primeros 500 chars): {str(body)[:500]}")
        
        # Normalizar el body: puede venir como lista directamente o envuelto en un objeto
        if isinstance(body, list):
            horas_aprobadas = body
        elif isinstance(body, dict):
            # Si viene como objeto, intentar extraer la lista
            if 'horas_aprobadas' in body:
                horas_aprobadas = body['horas_aprobadas']
            elif 'data' in body:
                horas_aprobadas = body['data']
            else:
                # Si es un objeto único, convertirlo a lista
                horas_aprobadas = [body]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de datos inválido. Se espera una lista o un objeto. Recibido: {type(body).__name__}"
            )
        
        # Validar que sea una lista
        if not isinstance(horas_aprobadas, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los datos deben ser una lista de horas aprobadas"
            )
        
        if len(horas_aprobadas) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron horas aprobadas"
            )
        
        print(f"✅ Datos normalizados: {len(horas_aprobadas)} entradas")
        
    except ValueError as e:
        # Error al parsear JSON
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al parsear JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error procesando request: {str(e)}"
        )
    
    if USE_FINANZAS_MOCK:
        # Usar mock
        try:
            print(f"🔄 Llamando a mock_finanzas_calcular_costos con {len(horas_aprobadas)} entradas")
            resultado = mock_finanzas_calcular_costos(horas_aprobadas)
            print(f"✅ Mock retornó {len(resultado)} roles")
            return resultado
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            error_msg = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
            error_trace = traceback.format_exc()
            print(f"❌ Error en mock de finanzas: {error_msg}")
            print(f"📋 Traceback completo:\n{error_trace}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en mock de finanzas: {error_msg}"
            )
    else:
        # Llamar a la API real de finanzas usando GET /api/tarifas
        print(f"🌐 Intentando obtener tarifas del módulo de finanzas en: {FINANZAS_API_BASE_URL}")
        print(f"📤 Procesando {len(horas_aprobadas)} entradas de horas aprobadas")
        try:
            resultado = await obtener_tarifas_finanzas(horas_aprobadas)
            print(f"✅ Tarifas obtenidas exitosamente: {len(resultado)} roles")
            return resultado
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            error_msg = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
            error_trace = traceback.format_exc()
            print(f"❌ Error inesperado obteniendo tarifas: {error_msg}")
            print(f"📋 Traceback completo:\n{error_trace}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error obteniendo tarifas del módulo de finanzas: {error_msg}"
            )

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Sistema de Carga de Horas PSA"}

@app.get("/")
def root():
    return {"service": "Sistema de Carga de Horas PSA", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)