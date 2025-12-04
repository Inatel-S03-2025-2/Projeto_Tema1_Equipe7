import pytest
from src.Controllers.userController import get_repo
from src.Database.models import UserModel
from src.main import app


# Mock para o Repositório
class MockRepository:
    def verifica_user(self, email):
        # Simula que o email já existe
        if email == "existente@teste.com":
            return UserModel(nickname="antigo", email="existente@teste.com", vetor_roles=[])
        return None

    def cadastro_user(self, user):
        user.id = 1
        return user

    def buscar_por_nickname(self, nickname):
        # Simula encontrar apenas se o nickname for "user_teste"
        if nickname == "user_teste":
            return UserModel(nickname="user_teste", email="teste@teste.com", vetor_roles=[])
        return None

    def alterar_user(self, user):
        return user

    def remove_user(self, user_id):
        # O controller verifica a existência pelo buscar_por_nickname antes de chamar remove_user
        return True


# Fixture que substitui o Repositório real pelo Mock
@pytest.fixture
def client_com_mock(client):
    app.dependency_overrides[get_repo] = lambda: MockRepository()
    yield client
    app.dependency_overrides = {}


# --- TESTES DE SUCESSO ---

def test_cadastrar_sucesso(client_com_mock):
    response = client_com_mock.post(
        "/users/cadastrar",
        params={"nickname": "novo", "email": "novo@teste.com", "senha": "123"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Usuário cadastrado com sucesso!"


def test_buscar_sucesso(client_com_mock):
    response = client_com_mock.get("/users/buscar/user_teste")
    assert response.status_code == 200
    assert response.json()["nickname"] == "user_teste"


# --- TESTES DE ERRO ---

def test_cadastrar_duplicado(client_com_mock):
    """Testa erro ao tentar cadastrar email que já existe"""
    response = client_com_mock.post(
        "/users/cadastrar",
        params={"nickname": "novo", "email": "existente@teste.com", "senha": "123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário com este e-mail já existe"


def test_buscar_nao_encontrado(client_com_mock):
    """Testa busca por um usuário que não existe"""
    response = client_com_mock.get("/users/buscar/fantasma")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"


def test_atualizar_nao_encontrado(client_com_mock):
    """Testa tentar atualizar um usuário que não existe"""
    response = client_com_mock.put(
        "/users/atualizar/fantasma",
        params={"novo_email": "novo@email.com"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"


def test_deletar_nao_encontrado(client_com_mock):
    """Testa tentar deletar um usuário que não existe"""
    response = client_com_mock.delete("/users/deletar/fantasma")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"