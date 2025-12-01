from datetime import date
from unittest.mock import MagicMock
from config.config import RECURSO_ID_DESARROLLO

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Sistema de Carga de Horas PSA"}

def test_obtener_mis_tareas(client, mock_external_api):
    mock_external_api.get_tareas_por_recurso.return_value = [
        {"id": "T1", "nombre": "Tarea 1"},
        {"id": "T2", "nombre": "Tarea 2"}
    ]

    response = client.get("/api/tareas/me")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_external_api.get_tareas_por_recurso.assert_called_with(RECURSO_ID_DESARROLLO)

def test_cargar_horas_endpoint(client, mock_db_session, mock_external_api):
    mock_val_res = MagicMock()
    mock_val_res.scalar.return_value = 0
    
    mock_ins_res = MagicMock()
    mock_ins_res.fetchone.return_value = ["UUID-123", "2023-10-27T10:00:00"]
    
    mock_db_session.execute.side_effect = [mock_val_res, mock_ins_res]

    payload = {
        "tarea_id": "TAREA-1",
        "proyecto_id": "PROY-1",
        "fecha": str(date.today()),
        "horas": 5.5,
        "descripcion": "Trabajo de endpoint"
    }

    response = client.post("/api/horas", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "UUID-123"
    assert data["horas"] == 5.5

def test_cargar_horas_invalido_max_24(client):
    payload = {
        "tarea_id": "TAREA-1",
        "proyecto_id": "PROY-1",
        "fecha": str(date.today()),
        "horas": 25, 
        "descripcion": "Exagerado"
    }

    response = client.post("/api/horas", json=payload)
    assert response.status_code == 422 