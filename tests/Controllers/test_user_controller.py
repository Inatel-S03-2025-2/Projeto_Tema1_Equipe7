import pytest
from src.controllers.user_controller import UserController
from src.models.user import User
from datetime import datetime, timezone
from unittest.mock import ANY


# Fixture para os mocks
@pytest.fixture
def mock_deps(mocker):
    mock_repo = mocker.Mock()
    mock_auth_controller = mocker.Mock()
    return mock_repo, mock_auth_controller


# Fixture para um usuário mock
@pytest.fixture
def mock_user():
    return User(
        id=1,
        nickname="novo_user",
        email="novo@exemplo.com",
        senha_hash="hash_gerado_pelo_auth",
        first_data_login=None,
        data_criacao=datetime.now(timezone.utc),
        vetor_roles=["user"]
    )


def test_cadastrar_sucesso(mock_deps, mock_user):
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o email não existe
    mock_repo.verifica_user.return_value = None
    # Simula que o auth_controller hasheou a senha
    mock_auth_controller.hash_senha.return_value = "hash_gerado_pelo_auth"
    # Simula que o repositório criou e retornou o usuário
    mock_repo.cadastro_user.return_value = mock_user

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    novo_usuario = controller.cadastrar(
        nickname="novo_user",
        email="novo@exemplo.com",
        senha="senha123"
    )

    assert novo_usuario == mock_user
    assert novo_usuario.email == "novo@exemplo.com"

    # Verifica as chamadas dos mocks
    mock_repo.verifica_user.assert_called_once_with(email="novo@exemplo.com")
    # Verifica se o AuthController foi chamado para hashear
    mock_auth_controller.hash_senha.assert_called_once_with("senha123")
    # Verifica se o repositório foi chamado com os dados corretos
    mock_repo.cadastro_user.assert_called_once_with({
        "nickname": "novo_user",
        "email": "novo@exemplo.com",
        "senha_hash": "hash_gerado_pelo_auth",
        "first_data_login": None,
        "data_criacao": ANY,
        "vetor_roles": ["user"]
    })


def test_cadastrar_email_ja_existe(mock_deps, mock_user):
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o email já existe
    mock_repo.verifica_user.return_value = mock_user

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    with pytest.raises(ValueError, match="Email já cadastrado"):
        controller.cadastrar(nickname="outro", email="novo@exemplo.com", senha="123")

    # Garante que o hash e o cadastro nem foram chamados
    mock_auth_controller.hash_senha.assert_not_called()
    mock_repo.cadastro_user.assert_not_called()



def test_buscar_sucesso(mock_deps, mock_user):
    mock_repo, mock_auth_controller = mock_deps

    mock_repo.buscar_user_por_id.return_value = mock_user

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    user_encontrado = controller.buscar(user_id=1)

    assert user_encontrado == mock_user
    mock_repo.buscar_user_por_id.assert_called_once_with(user_id=1)


def test_listar_sucesso(mock_deps, mock_user):
    mock_repo, mock_auth_controller = mock_deps
    mock_repo.listar_users.return_value = [mock_user, mock_user]

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    lista = controller.listar()

    assert len(lista) == 2
    mock_repo.listar_users.assert_called_once()