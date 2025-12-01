import pytest
import requests
from external_apis.external_apis import ExternalApiClient, PROYECTOS_API

def test_get_proyecto_ok(requests_mock):
    client = ExternalApiClient()
    proyecto_id = "123"
    url = PROYECTOS_API
    
    mock_response = [
        {"id": "123", "nombre": "Proyecto Alpha"},
        {"id": "456", "nombre": "Proyecto Beta"}
    ]
    requests_mock.get(url, json=mock_response)

    resultado = client.get_proyecto(proyecto_id)
    
    assert resultado is not None
    assert resultado["id"] == "123"
    assert resultado["nombre"] == "Proyecto Alpha"

def test_get_proyecto_not_found(requests_mock):
    client = ExternalApiClient()
    url = PROYECTOS_API
    
    requests_mock.get(url, json=[])

    resultado = client.get_proyecto("999")
    assert resultado is None

def test_api_timeout(requests_mock):
    client = ExternalApiClient()
    client.timeout = 1 
    
    requests_mock.get(PROYECTOS_API, exc=requests.exceptions.ConnectTimeout)
    
    resultado = client._get(PROYECTOS_API)
    assert resultado is None