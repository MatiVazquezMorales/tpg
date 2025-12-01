import pytest
from decimal import Decimal
from datetime import date
from services.services import CargaHorasService
from fastapi import HTTPException
from unittest.mock import MagicMock

def test_validar_horas_diarias_ok(mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar.return_value = 5
    mock_db_session.execute.return_value = mock_result

    es_valido, total = CargaHorasService.validar_horas_diarias(
        mock_db_session, "REC-1", date.today(), Decimal("8.0")
    )

    assert es_valido is True
    assert total == 5

def test_validar_horas_diarias_excede(mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar.return_value = 20
    mock_db_session.execute.return_value = mock_result

    es_valido, total = CargaHorasService.validar_horas_diarias(
        mock_db_session, "REC-1", date.today(), Decimal("5.0")
    )

    assert es_valido is False
    assert total == 20

def test_crear_carga_hora_exito(mock_db_session, mock_external_api):
    carga_data = MagicMock()
    carga_data.proyecto_id = "PROY-1"
    carga_data.tarea_id = "TAREA-1"
    carga_data.fecha = date.today()
    carga_data.horas = Decimal("4.0")
    carga_data.descripcion = "Test carga"

    mock_validate_res = MagicMock()
    mock_validate_res.scalar.return_value = 0
    
    mock_insert_res = MagicMock()
    mock_insert_res.fetchone.return_value = ["UUID-NUEVO", "2023-01-01T00:00:00"]
    
    mock_db_session.execute.side_effect = [mock_validate_res, mock_insert_res]

    resultado = CargaHorasService.crear_carga_hora(mock_db_session, "REC-1", carga_data)

    assert resultado["id"] == "UUID-NUEVO"
    assert resultado["horas"] == 4.0
    mock_db_session.commit.assert_called_once()

def test_crear_carga_hora_proyecto_no_existe(mock_db_session, mock_external_api):
    mock_external_api.get_proyecto.return_value = None
    
    carga_data = MagicMock()
    carga_data.proyecto_id = "PROY-INEXISTENTE"
    
    with pytest.raises(HTTPException) as excinfo:
        CargaHorasService.crear_carga_hora(mock_db_session, "REC-1", carga_data)
    
    assert excinfo.value.status_code == 404
    assert "Proyecto no encontrado" in excinfo.value.detail