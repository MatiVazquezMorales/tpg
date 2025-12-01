from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional, List, Any, Dict
from decimal import Decimal


class CargaHoraCreate(BaseModel):
    tarea_id: str
    proyecto_id: str
    fecha: date
    horas: Decimal = Field(gt=0, le=24)
    descripcion: Optional[str] = None
    
    @validator('horas')
    def validar_horas(cls, v):
        if v <= 0 or v > 24:
            raise ValueError('Las horas deben estar entre 0 y 24')
        return round(v, 2)

class CargaHoraUpdate(BaseModel):
    horas: Optional[Decimal] = Field(None, gt=0, le=24)
    descripcion: Optional[str] = None
    
    @validator('horas')
    def validar_horas(cls, v):
        if v is not None and (v <= 0 or v > 24):
            raise ValueError('Las horas deben estar entre 0 y 24')
        return round(v, 2) if v is not None else v


class CargaHora(BaseModel):
    id: str
    recurso_id: str
    tarea_id: str
    proyecto_id: str
    fecha: date
    horas: Decimal
    descripcion: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CargaHoraDetalle(CargaHora):
    proyecto: Optional[Dict[str, Any]] = None
    tarea: Optional[Dict[str, Any]] = None
    recurso: Optional[Dict[str, Any]] = None


class EntradaProyecto(BaseModel):
    carga_id: str
    proyecto_id: str
    proyecto_nombre: str
    tarea_id: str
    tarea_nombre: str
    horas: Decimal
    descripcion: Optional[str] = None

class ResumenDiario(BaseModel):
    fecha: date
    dia_semana: str  
    total_horas: Decimal
    entradas: List[EntradaProyecto]

class CalendarioSemanal(BaseModel):
    recurso_id: str
    recurso_nombre: str
    fecha_inicio: date  
    fecha_fin: date     
    dias: List[ResumenDiario]
    total_semana: Decimal
    

class EstadisticasRecurso(BaseModel):
    recurso: Dict[str, Any]
    total_horas_mes_actual: Decimal
    total_horas_semana_actual: Decimal
    proyectos_activos: int
    promedio_horas_diarias: Decimal