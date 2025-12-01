import pytest
import sys
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient


BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

from main.main import app
from db.database import get_db
from external_apis.external_apis import api_client


@pytest.fixture
def mock_db_session():
    """Simula una sesión de base de datos de SQLAlchemy"""
    session = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_result.scalar.return_value = 0
    session.execute.return_value = mock_result
    return session

@pytest.fixture
def client(mock_db_session):
    """Cliente de pruebas de FastAPI con la DB mockeada"""
    def override_get_db():
        try:
            yield mock_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_external_api(mocker):
    """
    Mockea automáticamente todas las llamadas a las APIs externas
    para que no intenten conectar a internet durante los tests.
    """
    mocker.patch.object(api_client, 'get_proyecto', return_value={"id": "PROY-1", "nombre": "Proyecto Test"})
    mocker.patch.object(api_client, 'get_tarea', return_value={"id": "TAREA-1", "proyectoId": "PROY-1", "nombre": "Tarea Test"})
    mocker.patch.object(api_client, 'get_recurso', return_value={"id": "REC-1", "nombre": "Recurso Test", "rolId": "ROL-1"})
    mocker.patch.object(api_client, 'get_rol', return_value={"id": "ROL-1", "nombre": "Desarrollador", "experiencia": "Senior"})
    mocker.patch.object(api_client, 'get_tareas_por_recurso', return_value=[])
    mocker.patch.object(api_client, 'get_proyectos_por_recurso', return_value=[])
    return api_client