import pytest
from src.Controllers.auth_controller import AuthController
from src.Database.user import User
from datetime import datetime, timezone
import time


@pytest.fixture
def mock_user_valido():
    return User(
        id=1,
        nickname="teste_user",
        email="teste@exemplo.com",
        senha_hash="$2b$12$NqN.i.M8h0NctD.PGOV5Xun2d3lJd1gG1N.3O5.Fq3w.B.g8.j/mK",
        first_data_login=None,
        data_criacao=datetime.now(timezone.utc),
        vetor_roles=["user"]
    )


@pytest.fixture
def mock_repo(mocker):
    return mocker.Mock()


def test_hash_e_verificar_senha(mock_repo):
    # O AuthController precisa de um repo no init, mesmo que não o use aqui
    controller = AuthController(repository=mock_repo)
    senha = "minhasenha123"

    hash_gerado = controller.hash_senha(senha)

    assert hash_gerado != senha
    assert controller.verificar_senha(senha_plana=senha, senha_hash=hash_gerado) == True
    assert controller.verificar_senha(senha_plana="senha_errada", senha_hash=hash_gerado) == False


def test_gerar_e_verificar_token(mock_repo):
    controller = AuthController(repository=mock_repo)
    email = "teste@exemplo.com"

    token = controller.gerar_token(email)

    assert token is not None
    email_verificado = controller.verificar_token(token)
    assert email_verificado == email


def test_verificar_token_expirado(mock_repo, mocker):
    # Patcher o tempo de expiração
    mocker.patch('src.controllers.auth_controller.ACCESS_TOKEN_EXPIRE_MINUTES', 0.000001)
    controller = AuthController(repository=mock_repo)

    token = controller.gerar_token("expirado@teste.com")
    time.sleep(0.01)  # Espera o token expirar

    assert controller.verificar_token(token) is None


def test_verificar_email(mock_repo):
    controller = AuthController(repository=mock_repo)

    # Cenário 1: Email existe
    mock_repo.verifica_user.return_value = mocker.Mock(spec=User)  # Retorna um mock de User
    assert controller.verificar_email("existe@exemplo.com") == True
    mock_repo.verifica_user.assert_called_with(email="existe@exemplo.com")

    # Cenário 2: Email não existe
    mock_repo.verifica_user.return_value = None
    assert controller.verificar_email("naoexiste@exemplo.com") == False
    mock_repo.verifica_user.assert_called_with(email="naoexiste@exemplo.com")



def test_login_sucesso(mock_repo, mock_user_valido):
    # Configurar o mock do repositório
    mock_repo.verifica_user.return_value = mock_user_valido

    # Criar o controlador com o mock
    controller = AuthController(repository=mock_repo)

    token = controller.login(email="teste@exemplo.com", senha="senha_correta")

    assert token is not None

    # Verifica se o token é válido
    email_no_token = controller.verificar_token(token)
    assert email_no_token == "teste@exemplo.com"

    # Verifica se o repositório foi chamado
    mock_repo.verifica_user.assert_called_once_with(email="teste@exemplo.com")


def test_login_usuario_nao_encontrado(mock_repo):
    mock_repo.verifica_user.return_value = None
    controller = AuthController(repository=mock_repo)

    with pytest.raises(ValueError, match="Email ou senha inválidos"):
        controller.login(email="errado@exemplo.com", senha="123")


def test_login_senha_invalida(mock_repo, mock_user_valido):
    mock_repo.verifica_user.return_value = mock_user_valido
    controller = AuthController(repository=mock_repo)

    with pytest.raises(ValueError, match="Email ou senha inválidos"):
        controller.login(email="teste@exemplo.com", senha="senha_errada")