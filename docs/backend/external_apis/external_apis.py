import requests
from typing import List, Optional, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    PROYECTOS_API, 
    TAREAS_API, 
    RECURSOS_API, 
    CLIENTES_API, 
    ROLES_API,
    API_TIMEOUT
)

class ExternalApiClient:

    def __init__(self):
        self.timeout = API_TIMEOUT

    def _get(self, url: str) -> Any:
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error conectando a API externa ({url}): {e}")
            return None

    def _buscar_en_lista(self, url_base: str, item_id: str) -> Optional[Dict[str, Any]]:
       
        lista = self._get(url_base)
        if isinstance(lista, list):
            for item in lista:
                if str(item.get("id")) == str(item_id):
                    return item
        return None

    def get_proyectos_por_recurso(self, recurso_id: str) -> List[Dict[str, Any]]:
    
        tareas = self._get(f"{TAREAS_API}?recursoId={recurso_id}")
        
        if not tareas or not isinstance(tareas, list):
            tareas_all = self._get(TAREAS_API)
            if isinstance(tareas_all, list):
                tareas = [t for t in tareas_all if str(t.get('recursoId')) == str(recurso_id)]
            else:
                return []
        
        proyectos_ids = set(t.get('proyectoId') for t in tareas if t.get('proyectoId'))
        proyectos = []
        
        for pid in proyectos_ids:
            p = self.get_proyecto(pid)
            if p:
                proyectos.append(p)
                
        return proyectos

    def get_tareas_por_recurso(self, recurso_id: str) -> List[Dict[str, Any]]:
        
        url = f"{TAREAS_API}?recursoId={recurso_id}"
        tareas = self._get(url)
        
        if not tareas or not isinstance(tareas, list):
            return []
        
        tareas_filtradas = [
            t for t in tareas 
            if str(t.get('recursoId')) == str(recurso_id)
        ]
             
        return tareas_filtradas
    # -----------------------------

    def get_tareas_por_proyecto(self, proyecto_id: str) -> List[Dict[str, Any]]:
        url = f"{TAREAS_API}?proyectoId={proyecto_id}"
        data = self._get(url)
        
        if isinstance(data, list):
            if data and str(data[0].get('proyectoId')) != str(proyecto_id):
                 return [t for t in data if str(t.get('proyectoId')) == str(proyecto_id)]
            return data
            
        return []

    def get_proyecto(self, proyecto_id: str) -> Optional[Dict[str, Any]]:
        return self._buscar_en_lista(PROYECTOS_API, proyecto_id)

    def get_tarea(self, tarea_id: str) -> Optional[Dict[str, Any]]:
        return self._buscar_en_lista(TAREAS_API, tarea_id)

    def get_recurso(self, recurso_id: str) -> Optional[Dict[str, Any]]:
        return self._buscar_en_lista(RECURSOS_API, recurso_id)
        
    def get_cliente(self, cliente_id: str) -> Optional[Dict[str, Any]]:
        return self._buscar_en_lista(CLIENTES_API, cliente_id)

    def get_rol(self, rol_id: str) -> Optional[Dict[str, Any]]:
        return self._buscar_en_lista(ROLES_API, rol_id)

    def get_todos_los_recursos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los recursos/empleados de la API"""
        recursos = self._get(RECURSOS_API)
        if not recursos or not isinstance(recursos, list):
            return []
        
        # Enriquecer cada recurso con información del rol
        recursos_enriquecidos = []
        for recurso in recursos:
            recurso_copy = recurso.copy()
            if 'rolId' in recurso:
                rol_info = self.get_rol(recurso['rolId'])
                if rol_info:
                    exp = rol_info.get('experiencia', '')
                    rol_nombre = f"{rol_info.get('nombre', 'Empleado')} {exp}".strip()
                    recurso_copy['rol_nombre'] = rol_nombre
                else:
                    recurso_copy['rol_nombre'] = "Empleado"
            else:
                recurso_copy['rol_nombre'] = "Empleado"
            
            recursos_enriquecidos.append(recurso_copy)
        
        return recursos_enriquecidos

    def get_todos_los_proyectos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los proyectos de la API"""
        proyectos = self._get(PROYECTOS_API)
        if not proyectos or not isinstance(proyectos, list):
            return []
        return proyectos
    
    def contar_tareas_abiertas_proyecto(self, proyecto_id: str) -> int:
        """Cuenta las tareas abiertas de un proyecto"""
        tareas = self.get_tareas_por_proyecto(proyecto_id)
        if not tareas:
            return 0
        
        # Contar tareas abiertas (estado 'abierta' o 'en curso' o sin estado definido)
        tareas_abiertas = [
            t for t in tareas 
            if not t.get('estado') or 
               t.get('estado', '').lower() in ['abierta', 'en curso', 'abierto', 'pendiente']
        ]
        return len(tareas_abiertas)

api_client = ExternalApiClient()