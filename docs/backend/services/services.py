from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
import calendar
from models import models as schemas
from external_apis.external_apis import api_client

DIAS_SEMANA = {
    0: "Lunes",
    1: "Martes", 
    2: "Miercoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sabado",
    6: "Domingo"
}

class CargaHorasService:
    
    @staticmethod
    def validar_horas_diarias(
        db: Session, 
        recurso_id: str,  
        fecha: date, 
        nuevas_horas: Decimal, 
        excluir_id: Optional[str] = None 
    ) -> Tuple[bool, Decimal]:
        
        query = """
            SELECT COALESCE(SUM(horas), 0) as total
            FROM carga_horas
            WHERE recurso_id = :recurso_id 
              AND fecha = :fecha
        """
        
        params = {
            "recurso_id": recurso_id,
            "fecha": fecha
        }
        
        if excluir_id:
            query += " AND id != :excluir_id"
            params["excluir_id"] = excluir_id
        
        result = db.execute(text(query), params)
        total_actual = Decimal(str(result.scalar()))
        total_con_nuevas = total_actual + nuevas_horas
        
        return (total_con_nuevas <= 24, total_actual)
    
    @staticmethod
    def crear_carga_hora(
        db: Session, 
        recurso_id: str, 
        carga: schemas.CargaHoraCreate
    ) -> Dict[str, Any]:

        proyecto = api_client.get_proyecto(carga.proyecto_id)
        if not proyecto:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
        tarea = api_client.get_tarea(carga.tarea_id)
        if not tarea:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        
        if tarea.get('proyectoId') != carga.proyecto_id:
            raise HTTPException(status_code=400, detail="La tarea no pertenece al proyecto especificado")
        
        recurso = api_client.get_recurso(recurso_id)
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        
        es_valido, total_actual = CargaHorasService.validar_horas_diarias(
            db, recurso_id, carga.fecha, carga.horas
        )
        
        if not es_valido:
            raise HTTPException(
                status_code=400,
                detail=f"No se pueden cargar más de 24 horas en un día. Total actual: {total_actual} hs"
            )
        
        query = text("""
            INSERT INTO carga_horas 
                (recurso_id, tarea_id, proyecto_id, fecha, horas, descripcion)
            VALUES 
                (:recurso_id, :tarea_id, :proyecto_id, :fecha, :horas, :descripcion)
            RETURNING id, created_at
        """)
        
        result = db.execute(query, {
            "recurso_id": recurso_id,
            "tarea_id": carga.tarea_id,
            "proyecto_id": carga.proyecto_id,
            "fecha": carga.fecha,
            "horas": float(carga.horas),
            "descripcion": carga.descripcion
        })
        
        row = result.fetchone()
        
        nuevo_id = str(row[0])
        fecha_creacion = row[1]
        
        db.commit()
        
        return {
            "id": nuevo_id,
            "recurso_id": recurso_id,
            "tarea_id": carga.tarea_id,
            "proyecto_id": carga.proyecto_id,
            "fecha": carga.fecha,
            "horas": float(carga.horas),
            "descripcion": carga.descripcion,
            "created_at": fecha_creacion
        }
    
    @staticmethod
    def obtener_calendario_semanal(
        db: Session, 
        recurso_id: str, 
        fecha_referencia: date
    ) -> Dict[str, Any]:
        
        dias_desde_lunes = fecha_referencia.weekday()
        fecha_inicio = fecha_referencia - timedelta(days=dias_desde_lunes)
        fecha_fin = fecha_inicio + timedelta(days=6)
        
        recurso = api_client.get_recurso(recurso_id)
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        
        query = text("""
            SELECT 
                id, fecha, horas, descripcion,
                proyecto_id, tarea_id
            FROM carga_horas
            WHERE recurso_id = :recurso_id
              AND fecha BETWEEN :fecha_inicio AND :fecha_fin
            ORDER BY fecha ASC, created_at ASC 
        """)
        
        result = db.execute(query, {
            "recurso_id": recurso_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })
        
        proyectos_cache = {}
        tareas_cache = {}
        dias_dict = {}
        
        for row in result:
            carga_id = str(row[0])
            fecha = row[1]
            horas = Decimal(str(row[2]))
            descripcion = row[3]
            proyecto_id = str(row[4])
            tarea_id = str(row[5])
            
            if proyecto_id not in proyectos_cache:
                proyectos_cache[proyecto_id] = api_client.get_proyecto(proyecto_id)
            proyecto = proyectos_cache[proyecto_id]
            
            if tarea_id not in tareas_cache:
                tareas_cache[tarea_id] = api_client.get_tarea(tarea_id)
            tarea = tareas_cache[tarea_id]
            
            entrada = {
                "carga_id": carga_id,
                "proyecto_id": proyecto_id,
                "proyecto_nombre": proyecto.get('nombre', 'N/A') if proyecto else 'N/A',
                "tarea_id": tarea_id,
                "tarea_nombre": tarea.get('nombre', 'N/A') if tarea else 'N/A',
                "horas": float(horas),
                "descripcion": descripcion
            }
            
            fecha_str = str(fecha)
            if fecha_str not in dias_dict:
                dias_dict[fecha_str] = {
                    "fecha": fecha,
                    "dia_semana": DIAS_SEMANA[fecha.weekday()],
                    "total_horas": Decimal(0),
                    "entradas": []
                }
            
            dias_dict[fecha_str]["total_horas"] += horas
            dias_dict[fecha_str]["entradas"].append(entrada)
        
        dias = []
        total_semana = Decimal(0)
        fecha_actual = fecha_inicio
        
        for i in range(7):
            fecha_str = str(fecha_actual)
            if fecha_str in dias_dict:
                dia_info = dias_dict[fecha_str]
                total_semana += dia_info["total_horas"]
                dias.append({
                    "fecha": dia_info["fecha"],
                    "dia_semana": dia_info["dia_semana"],
                    "total_horas": float(dia_info["total_horas"]),
                    "entradas": dia_info["entradas"]
                })
            else:
                dias.append({
                    "fecha": fecha_actual,
                    "dia_semana": DIAS_SEMANA[fecha_actual.weekday()],
                    "total_horas": 0,
                    "entradas": []
                })
            fecha_actual += timedelta(days=1)
        
        return {
            "recurso_id": recurso_id,
            "recurso_nombre": f"{recurso.get('nombre', '')} {recurso.get('apellido', '')}".strip(),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "dias": dias,
            "total_semana": float(total_semana)
        }
    
    @staticmethod
    def obtener_estadisticas_recurso(
        db: Session,
        recurso_id: str 
    ) -> Dict[str, Any]:
        """Obtiene estadísticas generales de un recurso"""
        
        recurso = api_client.get_recurso(recurso_id)
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        
        hoy = date.today()
        inicio_mes = date(hoy.year, hoy.month, 1)
        dias_desde_lunes = hoy.weekday()
        inicio_semana = hoy - timedelta(days=dias_desde_lunes)
        
        query_mes = text("SELECT COALESCE(SUM(horas), 0) FROM carga_horas WHERE recurso_id = :recurso_id AND fecha >= :inicio_mes")
        result = db.execute(query_mes, {"recurso_id": recurso_id, "inicio_mes": inicio_mes})
        total_mes = Decimal(str(result.scalar()))
        
        query_semana = text("SELECT COALESCE(SUM(horas), 0) FROM carga_horas WHERE recurso_id = :recurso_id AND fecha >= :inicio_semana")
        result = db.execute(query_semana, {"recurso_id": recurso_id, "inicio_semana": inicio_semana})
        total_semana = Decimal(str(result.scalar()))
        
        query_proyectos = text("SELECT COUNT(DISTINCT proyecto_id) FROM carga_horas WHERE recurso_id = :recurso_id AND fecha >= :inicio_mes")
        result = db.execute(query_proyectos, {"recurso_id": recurso_id, "inicio_mes": inicio_mes})
        proyectos_activos = result.scalar()
        
        query_promedio = text("""
            SELECT COALESCE(AVG(total_dia), 0) FROM (
                SELECT SUM(horas) as total_dia FROM carga_horas 
                WHERE recurso_id = :recurso_id AND fecha >= :hace_30_dias 
                GROUP BY fecha HAVING SUM(horas) > 0
            ) dias_con_horas
        """)
        hace_30_dias = hoy - timedelta(days=30)
        result = db.execute(query_promedio, {"recurso_id": recurso_id, "hace_30_dias": hace_30_dias})
        promedio = Decimal(str(result.scalar()))
        
        return {
            "recurso": recurso,
            "total_horas_mes_actual": float(total_mes),
            "total_horas_semana_actual": float(total_semana),
            "proyectos_activos": proyectos_activos,
            "promedio_horas_diarias": float(promedio)
        }
    
    @staticmethod
    def obtener_horas_totales_proyecto(
        db: Session,
        proyecto_id: str
    ) -> float:
        """Obtiene el total de horas cargadas para un proyecto"""
        query = text("""
            SELECT COALESCE(SUM(horas), 0) 
            FROM carga_horas 
            WHERE proyecto_id = :proyecto_id
        """)
        result = db.execute(query, {"proyecto_id": proyecto_id})
        total = result.scalar()
        return float(total) if total else 0.0
    
    @staticmethod
    def obtener_horas_aprobadas_por_periodo(
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las horas aprobadas agrupadas por tarea, recurso y período (año/mes).
        Formato de salida para el módulo de finanzas.
        """
        query = text("""
            SELECT 
                tarea_id,
                recurso_id,
                EXTRACT(YEAR FROM fecha) as anio,
                EXTRACT(MONTH FROM fecha) as mes,
                SUM(horas) as horas_aprobadas
            FROM carga_horas
            GROUP BY tarea_id, recurso_id, EXTRACT(YEAR FROM fecha), EXTRACT(MONTH FROM fecha)
            ORDER BY tarea_id, recurso_id, anio, mes
        """)
        
        result = db.execute(query)
        
        # Agrupar por tarea_id y recurso_id
        datos_agrupados = {}
        
        for row in result:
            tarea_id = str(row[0])
            recurso_id = str(row[1])
            anio = int(row[2])
            mes = int(row[3])
            horas_aprobadas = float(row[4])
            
            clave = f"{tarea_id}_{recurso_id}"
            
            if clave not in datos_agrupados:
                datos_agrupados[clave] = {
                    "tareaId": tarea_id,
                    "recursoId": recurso_id,
                    "periodos": []
                }
            
            datos_agrupados[clave]["periodos"].append({
                "anio": anio,
                "mes": mes,
                "horas_aprobadas": horas_aprobadas
            })
        
        # Convertir a lista y ordenar periodos dentro de cada entrada
        resultado = []
        for clave in sorted(datos_agrupados.keys()):
            entrada = datos_agrupados[clave]
            # Ordenar periodos por año y mes
            entrada["periodos"].sort(key=lambda p: (p["anio"], p["mes"]))
            resultado.append(entrada)
        
        return resultado