import pytest
from fastapi.testclient import TestClient
from src.main import app

# Fixture que disponibiliza o cliente de API para todos os testes
@pytest.fixture(scope="function")
def client():
    """
    Cria uma instância do TestClient.
    Isso permite simular chamadas HTTP (GET, POST, etc.) para sua API.
    """
    with TestClient(app) as test_client:
        yield test_client