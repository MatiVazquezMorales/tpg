import requests
from typing import List, Optional, Dict, Any
import sys
import os

# Ajuste de path para importar config
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
    """
    Cliente para comunicarse con las APIs externas de PSA.
    Estrategia adaptada para Mocks: Obtiene listas completas y filtra en memoria
    para evitar errores 404 en endpoints de detalle (/id).
    """

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
        """
        Método auxiliar: Trae toda la lista de la API y busca el ID en memoria.
        Esto soluciona el error 404 cuando el Mock no soporta GET /recurso/{id}.
        """
        lista = self._get(url_base)
        if isinstance(lista, list):
            for item in lista:
                # Comparamos como string para evitar problemas de tipo
                if str(item.get("id")) == str(item_id):
                    return item
        return None

    def get_proyectos_por_recurso(self, recurso_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los proyectos asociados a un recurso.
        """
        # Intentamos filtrar por query param. Si el mock lo ignora, traerá todas.
        tareas = self._get(f"{TAREAS_API}?recursoId={recurso_id}")
        
        if not tareas or not isinstance(tareas, list):
            # Fallback: Si devuelve error o no es lista, traemos todas y filtramos manual
            tareas_all = self._get(TAREAS_API)
            if isinstance(tareas_all, list):
                tareas = [t for t in tareas_all if str(t.get('recursoId')) == str(recurso_id)]
            else:
                return []
        
        proyectos_ids = set(t.get('proyectoId') for t in tareas if t.get('proyectoId'))
        proyectos = []
        
        # Obtenemos el detalle de cada proyecto encontrado
        for pid in proyectos_ids:
            p = self.get_proyecto(pid)
            if p:
                proyectos.append(p)
                
        return proyectos

    # --- NUEVO MÉTODO AGREGADO ---
    def get_tareas_por_recurso(self, recurso_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene todas las tareas asignadas a un recurso específico.
        IMPORTANTE: Filtra manualmente la respuesta porque el Mock suele ignorar 
        los parámetros de URL y devuelve todas las tareas.
        """
        url = f"{TAREAS_API}?recursoId={recurso_id}"
        tareas = self._get(url)
        
        if not tareas or not isinstance(tareas, list):
            return []
            
        # FILTRADO MANUAL OBLIGATORIO
        # Recorremos toda la lista y nos quedamos solo con las que coinciden con el ID.
        tareas_filtradas = [
            t for t in tareas 
            if str(t.get('recursoId')) == str(recurso_id)
        ]
             
        return tareas_filtradas
    # -----------------------------

    def get_tareas_por_proyecto(self, proyecto_id: str) -> List[Dict[str, Any]]:
        """Obtiene las tareas de un proyecto específico"""
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

api_client = ExternalApiClient()