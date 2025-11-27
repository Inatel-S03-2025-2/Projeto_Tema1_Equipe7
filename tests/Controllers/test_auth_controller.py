import pytest
from src.Controllers.authController import authController, login as login_endpoint
from fastapi import HTTPException
import time


# Testes Unitários da Classe (Métodos Estáticos)

def test_hash_senha():
    senha = "senha123"
    hash1 = authController.hash_senha(senha)
    hash2 = authController.hash_senha(senha)
    # O hash deve ser determinístico ou verificável
    assert hash1 == hash2
    assert hash1 != senha


def test_verificar_senha():
    senha = "senha_secreta"
    hash_salvo = authController.hash_senha(senha)

    assert authController.verificar_senha(senha, hash_salvo) is True
    assert authController.verificar_senha("senha_errada", hash_salvo) is False


def test_verificar_email():
    assert authController.verificar_email("teste@email.com") is True
    assert authController.verificar_email("testeemail.com") is False  # Sem @
    assert authController.verificar_email("teste@com") is False  # Sem ponto (ajuste conforme lógica simples do código)
    # Nota: O código verifica apenas '@' e '.'


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


# Testes do Endpoint (Async)

@pytest.mark.asyncio
async def test_login_sucesso():
    # Testando com as credenciais hardcoded do seu código
    resultado = await login_endpoint("teste@email.com", "123")
    assert "token" in resultado


@pytest.mark.asyncio
async def test_login_credenciais_invalidas():
    with pytest.raises(HTTPException) as excinfo:
        await login_endpoint("errado@email.com", "senhaerrada")

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Credenciais inválidas"