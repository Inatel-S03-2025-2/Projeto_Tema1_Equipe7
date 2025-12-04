import pytest
from src.Controllers.authController import authController, login as login_endpoint, get_repo
from src.Database.models import UserModel
from fastapi import HTTPException
from src.main import app

# --- TESTES UNITÁRIOS (Lógica Pura) ---

def test_hash_senha():
    senha = "senha123"
    hash1 = authController.hash_senha(senha)
    hash2 = authController.hash_senha(senha)
    assert hash1 == hash2
    assert hash1 != senha

def test_verificar_senha():
    senha = "senha_secreta"
    hash_salvo = authController.hash_senha(senha)
    assert authController.verificar_senha(senha, hash_salvo) is True
    assert authController.verificar_senha("senha_errada", hash_salvo) is False

def test_verificar_email():
    assert authController.verificar_email("teste@email.com") is True
    assert authController.verificar_email("testeemail.com") is False

def test_gerar_e_verificar_token():
    email = "usuario@teste.com"
    token = authController.gerar_token(email)
    assert isinstance(token, str)
    dados = authController.verificar_token(token)
    assert dados["valid"] is True
    assert dados["email"] == email

def test_token_invalido():
    with pytest.raises(HTTPException):
        authController.verificar_token("token.invalido.aleatorio")

# --- TESTES DE INTEGRAÇÃO DO ENDPOINT (Com Mock de Banco) ---

# Mock do Repositório para simular o banco
class MockRepositoryAuth:
    def verifica_user(self, email):
        if email == "correto@email.com":
            # Retorna um usuário com a senha "123" hashada
            senha_hash = authController.hash_senha("123")
            return UserModel(email="correto@email.com", senha_hash=senha_hash, nickname="teste", vetor_roles=[])
        return None

@pytest.fixture
def client_auth(client):
    # Substitui o banco real pelo Mock
    app.dependency_overrides[get_repo] = lambda: MockRepositoryAuth()
    yield client
    app.dependency_overrides = {}

def test_login_sucesso(client_auth):
    # Tenta logar com o usuário que existe no Mock
    response = client_auth.post(
        "/auth/login",
        params={"email": "correto@email.com", "senha": "123"}
    )
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_usuario_inexistente(client_auth):
    response = client_auth.post(
        "/auth/login",
        params={"email": "naoexiste@email.com", "senha": "123"}
    )
    assert response.status_code == 401
    assert "Credenciais inválidas" in response.json()["detail"]

def test_login_senha_incorreta(client_auth):
    # Usuário existe, mas senha errada
    response = client_auth.post(
        "/auth/login",
        params={"email": "correto@email.com", "senha": "senhaerrada"}
    )
    assert response.status_code == 401
    assert "Credenciais inválidas" in response.json()["detail"]