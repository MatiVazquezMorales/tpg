from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID
from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
import calendar

from models import models as schemas
from external_apis.external_apis import api_client

# Mapeo de dias
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
    """Servicio para gestion de carga de horas"""
    
    @staticmethod
    def validar_horas_diarias(
        db: Session, 
        recurso_id: UUID, 
        fecha: date, 
        nuevas_horas: Decimal, 
        excluir_id: Optional[UUID] = None
    ) -> Tuple[bool, Decimal]:
        """
        Valida que no se excedan 24 horas en un dia.
        Retorna (es_valido, total_actual)
        """
        query = """
            SELECT COALESCE(SUM(horas), 0) as total
            FROM carga_horas
            WHERE recurso_id = :recurso_id 
              AND fecha = :fecha
        """
        
        params = {
            "recurso_id": str(recurso_id),
            "fecha": fecha
        }
        
        if excluir_id:
            query += " AND id != :excluir_id"
            params["excluir_id"] = str(excluir_id)
        
        result = db.execute(text(query), params)
        total_actual = Decimal(str(result.scalar()))
        total_con_nuevas = total_actual + nuevas_horas
        
        return (total_con_nuevas <= 24, total_actual)
    
    @staticmethod
    def crear_carga_hora(
        db: Session, 
        recurso_id: UUID, 
        carga: schemas.CargaHoraCreate
    ) -> Dict[str, Any]:
        """Crea una nueva carga de horas"""
        
        # Validar que el proyecto existe en la API externa
        proyecto = api_client.get_proyecto(str(carga.proyecto_id))
        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto no encontrado"
            )
        
        # Validar que la tarea existe
        tarea = api_client.get_tarea(str(carga.tarea_id))
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea no encontrada"
            )
        
        # Validar que la tarea pertenece al proyecto
        if tarea.get('proyectoId') != str(carga.proyecto_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La tarea no pertenece al proyecto especificado"
            )
        
        # Validar que el recurso existe
        recurso = api_client.get_recurso(str(recurso_id))
        if not recurso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recurso no encontrado"
            )
        
        # Validar horas diarias
        es_valido, total_actual = CargaHorasService.validar_horas_diarias(
            db, recurso_id, carga.fecha, carga.horas
        )
        
        if not es_valido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pueden cargar más de 24 horas en un día. "
                       f"Ya tienes {total_actual} horas cargadas en {carga.fecha}"
            )
        
        # Insertar carga de horas
        query = text("""
            INSERT INTO carga_horas 
                (recurso_id, tarea_id, proyecto_id, fecha, horas, descripcion)
            VALUES 
                (:recurso_id, :tarea_id, :proyecto_id, :fecha, :horas, :descripcion)
            RETURNING id, created_at
        """)
        
        result = db.execute(query, {
            "recurso_id": str(recurso_id),
            "tarea_id": str(carga.tarea_id),
            "proyecto_id": str(carga.proyecto_id),
            "fecha": carga.fecha,
            "horas": float(carga.horas),
            "descripcion": carga.descripcion
        })
        
        row = result.fetchone()
        db.commit()
        
        return {
            "id": str(row[0]),
            "recurso_id": str(recurso_id),
            "tarea_id": str(carga.tarea_id),
            "proyecto_id": str(carga.proyecto_id),
            "fecha": carga.fecha,
            "horas": float(carga.horas),
            "descripcion": carga.descripcion,
            "created_at": row[1]
        }
    
    @staticmethod
    def obtener_calendario_semanal(
        db: Session, 
        recurso_id: UUID, 
        fecha_referencia: date
    ) -> Dict[str, Any]:
        """
        Obtiene el calendario semanal de un recurso.
        La fecha_referencia se ajusta automáticamente al lunes de esa semana.
        """
        
        # Ajustar al lunes de la semana
        dias_desde_lunes = fecha_referencia.weekday()
        fecha_inicio = fecha_referencia - timedelta(days=dias_desde_lunes)
        fecha_fin = fecha_inicio + timedelta(days=6)
        
        # Obtener recurso
        recurso = api_client.get_recurso(str(recurso_id))
        if not recurso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurso no encontrado"
            )
        
        # Obtener todas las cargas de la semana
        query = text("""
            SELECT 
                id, fecha, horas, descripcion,
                proyecto_id, tarea_id
            FROM carga_horas
            WHERE recurso_id = :recurso_id
              AND fecha BETWEEN :fecha_inicio AND :fecha_fin
            ORDER BY fecha, proyecto_id
        """)
        
        result = db.execute(query, {
            "recurso_id": str(recurso_id),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })
        
        # Obtener proyectos y tareas (cachear para no hacer requests repetidos)
        proyectos_cache = {}
        tareas_cache = {}
        
        # Organizar por dia
        dias_dict = {}
        
        for row in result:
            carga_id = row[0]
            fecha = row[1]
            horas = Decimal(str(row[2]))
            descripcion = row[3]
            proyecto_id = str(row[4])
            tarea_id = str(row[5])
            
            # Obtener proyecto (con cache)
            if proyecto_id not in proyectos_cache:
                proyectos_cache[proyecto_id] = api_client.get_proyecto(proyecto_id)
            proyecto = proyectos_cache[proyecto_id]
            
            # Obtener tarea (con cache)
            if tarea_id not in tareas_cache:
                tareas_cache[tarea_id] = api_client.get_tarea(tarea_id)
            tarea = tareas_cache[tarea_id]
            
            # Crear entrada
            entrada = {
                "carga_id": str(carga_id),
                "proyecto_id": proyecto_id,
                "proyecto_nombre": proyecto.get('nombre', 'N/A') if proyecto else 'N/A',
                "tarea_id": tarea_id,
                "tarea_nombre": tarea.get('nombre', 'N/A') if tarea else 'N/A',
                "horas": float(horas),
                "descripcion": descripcion
            }
            
            # Agregar al día correspondiente
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
        
        # Crear lista de 7 dias (incluir dias sin cargas)
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
            "recurso_id": str(recurso_id),
            "recurso_nombre": f"{recurso.get('nombre', '')} {recurso.get('apellido', '')}".strip(),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "dias": dias,
            "total_semana": float(total_semana)
        }
    
    @staticmethod
    def obtener_estadisticas_recurso(
        db: Session,
        recurso_id: UUID
    ) -> Dict[str, Any]:
        """Obtiene estadísticas generales de un recurso"""
        
        # Obtener recurso
        recurso = api_client.get_recurso(str(recurso_id))
        if not recurso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurso no encontrado"
            )
        
        hoy = date.today()
        
        # Inicio del mes actual
        inicio_mes = date(hoy.year, hoy.month, 1)
        
        # Inicio de la semana actual (lunes)
        dias_desde_lunes = hoy.weekday()
        inicio_semana = hoy - timedelta(days=dias_desde_lunes)
        
        # Total horas del mes
        query_mes = text("""
            SELECT COALESCE(SUM(horas), 0)
            FROM carga_horas
            WHERE recurso_id = :recurso_id
              AND fecha >= :inicio_mes
        """)
        
        result = db.execute(query_mes, {
            "recurso_id": str(recurso_id),
            "inicio_mes": inicio_mes
        })
        total_mes = Decimal(str(result.scalar()))
        
        # Total horas de la semana
        query_semana = text("""
            SELECT COALESCE(SUM(horas), 0)
            FROM carga_horas
            WHERE recurso_id = :recurso_id
              AND fecha >= :inicio_semana
        """)
        
        result = db.execute(query_semana, {
            "recurso_id": str(recurso_id),
            "inicio_semana": inicio_semana
        })
        total_semana = Decimal(str(result.scalar()))
        
        # Proyectos activos (con horas en el mes)
        query_proyectos = text("""
            SELECT COUNT(DISTINCT proyecto_id)
            FROM carga_horas
            WHERE recurso_id = :recurso_id
              AND fecha >= :inicio_mes
        """)
        
        result = db.execute(query_proyectos, {
            "recurso_id": str(recurso_id),
            "inicio_mes": inicio_mes
        })
        proyectos_activos = result.scalar()
        
        # Promedio de horas diarias (últimos 30 días con horas)
        query_promedio = text("""
            SELECT COALESCE(AVG(total_dia), 0)
            FROM (
                SELECT SUM(horas) as total_dia
                FROM carga_horas
                WHERE recurso_id = :recurso_id
                  AND fecha >= :hace_30_dias
                GROUP BY fecha
                HAVING SUM(horas) > 0
            ) dias_con_horas
        """)
        
        hace_30_dias = hoy - timedelta(days=30)
        result = db.execute(query_promedio, {
            "recurso_id": str(recurso_id),
            "hace_30_dias": hace_30_dias
        })
        promedio = Decimal(str(result.scalar()))
        
        return {
            "recurso": recurso,
            "total_horas_mes_actual": float(total_mes),
            "total_horas_semana_actual": float(total_semana),
            "proyectos_activos": proyectos_activos,
            "promedio_horas_diarias": float(promedio)
        }