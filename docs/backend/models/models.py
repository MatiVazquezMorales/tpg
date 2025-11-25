from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional, List, Any, Dict
from decimal import Decimal
from uuid import UUID

# Modelos de entrada de datos

class CargaHoraCreate(BaseModel):
    """Modelo para crear una carga de horas"""
    tarea_id: UUID
    proyecto_id: UUID
    fecha: date
    #gt = greater than
    #le = less than or equal to
    horas: Decimal = Field(gt=0, le=24, decimal_places=2)
    descripcion: Optional[str] = None
    
    #validacion con decorador para el campo horas
    @validator('horas')
    def validar_horas(cls, v):
        if v <= 0 or v > 24:
            raise ValueError('Las horas deben estar entre 0 y 24')
        return round(v, 2)

class CargaHoraUpdate(BaseModel):
    """Modelo para actualizar una carga de horas"""
    horas: Optional[Decimal] = Field(None, gt=0, le=24, decimal_places=2)
    descripcion: Optional[str] = None
    
    @validator('horas')
    def validar_horas(cls, v):
        if v is not None and (v <= 0 or v > 24):
            raise ValueError('Las horas deben estar entre 0 y 24')
        return round(v, 2) if v is not None else v

# Modelos de respuesta de datos

class CargaHora(BaseModel):
    """Modelo de respuesta para una carga de horas"""
    id: UUID
    recurso_id: UUID
    tarea_id: UUID
    proyecto_id: UUID
    fecha: date
    horas: Decimal
    descripcion: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CargaHoraDetalle(CargaHora):
    """Carga de horas con información enriquecida de las APIs externas"""
    proyecto: Optional[Dict[str, Any]] = None
    tarea: Optional[Dict[str, Any]] = None
    recurso: Optional[Dict[str, Any]] = None

# Modelos para calendario de horas

class EntradaProyecto(BaseModel):
    """Una entrada de horas en un proyecto/tarea para un día específico"""
    carga_id: UUID
    proyecto_id: UUID
    proyecto_nombre: str
    tarea_id: UUID
    tarea_nombre: str
    horas: Decimal
    descripcion: Optional[str] = None

class ResumenDiario(BaseModel):
    """Resumen de horas de un día específico"""
    fecha: date
    dia_semana: str  # "Lunes", "Martes", etc.
    total_horas: Decimal
    entradas: List[EntradaProyecto]

class CalendarioSemanal(BaseModel):
    """Calendario completo de una semana"""
    recurso_id: UUID
    recurso_nombre: str
    fecha_inicio: date  # Lunes
    fecha_fin: date     # Domingo
    dias: List[ResumenDiario]
    total_semana: Decimal
    
# Modelos para estadisticas

class EstadisticasRecurso(BaseModel):
    """Estadísticas generales de un recurso"""
    recurso: Dict[str, Any]
    total_horas_mes_actual: Decimal
    total_horas_semana_actual: Decimal
    proyectos_activos: int
    promedio_horas_diarias: Decimal