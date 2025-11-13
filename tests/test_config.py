import pytest
from fastapi.testclient import TestClient

# 1. Importa o app principal
from src.main import app

# 2. Importa o banco de dados fake para podermos limpá-lo
from src.Controllers.userController import fake_db

@pytest.fixture(scope="function")
def reset_db():
    fake_db.clear()
    yield # O teste roda aqui
    fake_db.clear() # Limpa depois também

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client