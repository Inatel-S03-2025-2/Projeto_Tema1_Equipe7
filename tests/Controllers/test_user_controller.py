import pytest
from unittest.mock import MagicMock, patch
from src.Controllers.userController import userController
from src.Database.user import User
from datetime import datetime
from fastapi import HTTPException


# Fixture para um usuário padrão
@pytest.fixture
def mock_user_model():
    return User(
        id=1,
        nickname="novo_user",
        email="novo@exemplo.com",
        senha_hash="hash_simulado",
        first_data_login=None,
        data_criacao=datetime.now(),
        vetor_roles=[]
    )


@pytest.mark.asyncio
async def test_cadastrar_sucesso(mock_user_model):
    # Patcha o objeto 'repo' que está instanciado dentro do userController.py
    with patch("src.Controllers.userController.repo") as mock_repo:
        # Simula que o usuário não existe (para permitir cadastro)
        mock_repo.verifica_user.return_value = None
        mock_repo.cadastro_user.return_value = None

        response = await userController.cadastrar(
            nickname="novo_user",
            email="novo@exemplo.com",
            senha="123"
        )

        assert response["message"] == "Usuário cadastrado com sucesso!"
        assert response["user"].email == "novo@exemplo.com"

        mock_repo.verifica_user.assert_called_once_with("novo@exemplo.com")
        mock_repo.cadastro_user.assert_called_once()


@pytest.mark.asyncio
async def test_cadastrar_erro_duplicado():
    with patch("src.Controllers.userController.repo") as mock_repo:
        # Simula que o usuário já existe
        mock_repo.verifica_user.return_value = True

        with pytest.raises(HTTPException) as excinfo:
            await userController.cadastrar("user", "duplicado@teste.com", "123")

        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Usuário com este e-mail já existe"


@pytest.mark.asyncio
async def test_buscar_sucesso(mock_user_model):
    with patch("src.Controllers.userController.repo") as mock_repo:
        # O controller itera sobre a lista retornada por listar_users
        mock_repo.listar_users.return_value = [mock_user_model]

        resultado = await userController.buscar("novo_user")

        assert resultado == mock_user_model
        assert resultado.nickname == "novo_user"


@pytest.mark.asyncio
async def test_buscar_nao_encontrado():
    with patch("src.Controllers.userController.repo") as mock_repo:
        mock_repo.listar_users.return_value = []

        with pytest.raises(HTTPException) as excinfo:
            await userController.buscar("fantasma")

        assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_sucesso(mock_user_model):
    with patch("src.Controllers.userController.repo") as mock_repo:
        mock_repo.listar_users.return_value = [mock_user_model]

        resultado = await userController.atualizar("novo_user", novo_email="email@novo.com")

        assert resultado["message"] == "Usuário atualizado com sucesso!"
        assert resultado["user"].email == "email@novo.com"
        mock_repo.alterar_user.assert_called_once()


@pytest.mark.asyncio
async def test_listar_sucesso(mock_user_model):
    with patch("src.Controllers.userController.repo") as mock_repo:
        mock_repo.listar_users.return_value = [mock_user_model, mock_user_model]

        resultado = await userController.listar()

        assert len(resultado) == 2


@pytest.mark.asyncio
async def test_deletar_sucesso(mock_user_model):
    with patch("src.Controllers.userController.repo") as mock_repo:
        mock_repo.listar_users.return_value = [mock_user_model]

        # O controller acessa repo._fake_db.remove(user).
        # Precisamos criar esse atributo no mock.
        mock_repo._fake_db = MagicMock()

        response = await userController.deletar("novo_user")

        assert response["message"] == "Usuário deletado com sucesso!"
        # Verifica se o metodo remove foi chamado na lista fake
        mock_repo._fake_db.remove.assert_called_once_with(mock_user_model)