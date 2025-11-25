"""
Configuración para el sistema de carga de horas.
Modifica estos valores según tu entorno de desarrollo.
"""
import os
from uuid import UUID

# BASE DE DATOS

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://usuario:password@localhost:5432/timesheet_db"
)

# USUARIO DE DESARROLLO 

# ID del recurso que se usará para todas las operaciones
# Cambia este valor por el ID del recurso con el que quieras trabajar
RECURSO_ID_DESARROLLO = "ff14a491-e26d-4092-86ea-d76f20c165d1"  # Martin Garcia

# Recursos disponibles en la API mock:
# - ff14a491-e26d-4092-86ea-d76f20c165d1 (Martin Garcia)
# - 2e6ecd47-fa18-490e-b25a-c9101a398b6d (Lucia Perez)
# - 47f744bb-0553-497a-b6e3-fdb64ddaca2a (Mariana Juarez)
# - a21147f8-6538-46d8-95ac-9ddf95ff8c29 (Horacio Martinez)

def get_recurso_id_desarrollo() -> UUID:
    """Retorna el UUID del recurso de desarrollo"""
    return UUID(RECURSO_ID_DESARROLLO)

# APIs EXTERNAS 

RECURSOS_API = "https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/32c8fe38-22a6-4fbb-b461-170dfac937e4/recursos-api/1.0.1/m/recursos"
CLIENTES_API = "https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/754f50e8-20d8-4223-bbdc-56d50131d0ae/clientes-psa/1.0.0/m/api/clientes"
TAREAS_API = "https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/32c8fe38-22a6-4fbb-b461-170dfac937e4/tareas-api/1.0.0/m/tareas"
ROLES_API = "https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/32c8fe38-22a6-4fbb-b461-170dfac937e4/roles-api/1.0.0/m/roles"
PROYECTOS_API = "https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/32c8fe38-22a6-4fbb-b461-170dfac937e4/proyectos-api/1.0.0/m/proyectos"

# CONFIGURACIÓN DE LA APLICACIÓN 

# Puerto donde corre el servidor
PORT = int(os.getenv("PORT", 8000))

# Nivel de logs
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# CORS - Dominios permitidos
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Timeout para requests a APIs externas (segundos)
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 10))