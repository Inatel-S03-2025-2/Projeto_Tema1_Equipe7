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

# TESTES DE DELEÇÃO DE USUÁRIO

def test_deletar_sucesso(mock_deps, mock_user):
    """Testa a deleção bem-sucedida de um usuário existente"""
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o usuário existe ao buscar
    mock_repo.buscar_user_por_id.return_value = mock_user
    # Simula que a deleção foi bem-sucedida
    mock_repo.deletar_user.return_value = True

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    resultado = controller.deletar(user_id=1)

    # Verifica que retornou sucesso
    assert resultado == True
    # Verifica que buscou o usuário antes de deletar
    mock_repo.buscar_user_por_id.assert_called_once_with(user_id=1)
    # Verifica que chamou o método de deleção
    mock_repo.deletar_user.assert_called_once_with(user_id=1)


def test_deletar_usuario_nao_encontrado(mock_deps):
    """Testa tentativa de deletar um usuário que não existe"""
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o usuário não existe
    mock_repo.buscar_user_por_id.return_value = None

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    # Deve lançar erro ao tentar deletar usuário inexistente
    with pytest.raises(ValueError, match="Usuário não encontrado"):
        controller.deletar(user_id=999)

    # Verifica que tentou buscar o usuário
    mock_repo.buscar_user_por_id.assert_called_once_with(user_id=999)
    # Verifica que NÃO chamou o método de deleção
    mock_repo.deletar_user.assert_not_called()

# TESTES DE ATUALIZAÇÃO DE USUÁRIO

def test_atualizar_sucesso(mock_deps, mock_user):
    """Testa a atualização bem-sucedida de dados de um usuário"""
    mock_repo, mock_auth_controller = mock_deps

    # Cria uma versão atualizada do usuário
    usuario_atualizado = User(
        id=1,
        nickname="novo_user",
        email="email_atualizado@exemplo.com",  # Email foi atualizado
        senha_hash="hash_gerado_pelo_auth",
        first_data_login=None,
        data_criacao=datetime.now(timezone.utc),
        vetor_roles=["user"]
    )

    # Simula que o usuário existe
    mock_repo.buscar_user_por_id.return_value = mock_user
    # Simula que a atualização foi bem-sucedida
    mock_repo.alterar_user.return_value = usuario_atualizado

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    resultado = controller.atualizar(
        user_id=1,
        novo_email="email_atualizado@exemplo.com"
    )

    # Verifica que o email foi atualizado
    assert resultado.email == "email_atualizado@exemplo.com"
    # Verifica que buscou o usuário antes de atualizar
    mock_repo.buscar_user_por_id.assert_called_once_with(user_id=1)
    # Verifica que chamou o método de atualização
    mock_repo.alterar_user.assert_called_once()


def test_atualizar_usuario_nao_encontrado(mock_deps):
    """Testa tentativa de atualizar um usuário que não existe"""
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o usuário não existe
    mock_repo.buscar_user_por_id.return_value = None

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    # Deve lançar erro ao tentar atualizar usuário inexistente
    with pytest.raises(ValueError, match="Usuário não encontrado"):
        controller.atualizar(user_id=999, novo_email="novo@exemplo.com")

    # Verifica que tentou buscar o usuário
    mock_repo.buscar_user_por_id.assert_called_once_with(user_id=999)
    # Verifica que NÃO chamou o método de atualização
    mock_repo.alterar_user.assert_not_called()


def test_atualizar_sem_alteracoes(mock_deps, mock_user):
    """Testa atualização quando nenhum dado novo é fornecido"""
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o usuário existe
    mock_repo.buscar_user_por_id.return_value = mock_user
    mock_repo.alterar_user.return_value = mock_user  # Retorna sem alterações

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    # Chama atualizar sem passar novos dados
    resultado = controller.atualizar(user_id=1)

    # Deve retornar o usuário sem modificações
    assert resultado == mock_user
    assert resultado.email == "novo@exemplo.com"  # Email original


# TESTES DE BUSCA COM USUÁRIO NÃO ENCONTRADO

def test_buscar_usuario_nao_encontrado(mock_deps):
    """Testa busca de um usuário inexistente"""
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o usuário não existe
    mock_repo.buscar_user_por_id.return_value = None

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    # Deve lançar erro ao buscar usuário inexistente
    with pytest.raises(ValueError, match="Usuário não encontrado"):
        controller.buscar(user_id=999)

    # Verifica que tentou buscar no repositório
    mock_repo.buscar_user_por_id.assert_called_once_with(user_id=999)


def test_buscar_com_id_invalido(mock_deps):
    """Testa busca com IDs inválidos (negativo, zero, None)"""
    mock_repo, mock_auth_controller = mock_deps

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    ids_invalidos = [-1, 0, None]

    for id_invalido in ids_invalidos:
        # Deve lançar erro para IDs inválidos
        with pytest.raises((ValueError, TypeError)):
            controller.buscar(user_id=id_invalido)

# TESTES DE VALIDAÇÃO DE DADOS NO CADASTRO

def test_cadastrar_com_nickname_vazio(mock_deps):
    """Testa cadastro com nickname vazio ou None"""
    mock_repo, mock_auth_controller = mock_deps

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    # Testa nickname vazio
    with pytest.raises(ValueError, match="Nickname.*inválido|vazio|obrigatório"):
        controller.cadastrar(nickname="", email="test@test.com", senha="senha123")

    # Testa nickname None
    with pytest.raises((ValueError, TypeError)):
        controller.cadastrar(nickname=None, email="test@test.com", senha="senha123")

    # Garante que nenhum cadastro foi realizado
    mock_repo.cadastro_user.assert_not_called()


def test_cadastrar_com_email_invalido(mock_deps):
    """Testa cadastro com formatos de email inválidos"""
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o auth_controller valida o formato do email
    mock_auth_controller.verificar_email.return_value = False

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    emails_invalidos = [
        "semArroba.com",
        "sem@ponto",
        "@semNome.com",
        "",
        "duplo@@email.com"
    ]

    for email_invalido in emails_invalidos:
        # Deve lançar erro para emails inválidos
        with pytest.raises(ValueError, match="Email.*inválido"):
            controller.cadastrar(
                nickname="user_teste",
                email=email_invalido,
                senha="senha123"
            )

    # Garante que nenhum cadastro foi realizado
    mock_repo.cadastro_user.assert_not_called()


def test_cadastrar_com_senha_vazia(mock_deps):
    """Testa cadastro com senha vazia ou muito curta"""
    mock_repo, mock_auth_controller = mock_deps

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    # Testa senha vazia
    with pytest.raises(ValueError, match="Senha.*inválida|vazia|obrigatória"):
        controller.cadastrar(nickname="user_teste", email="test@test.com", senha="")

    # Testa senha None
    with pytest.raises((ValueError, TypeError)):
        controller.cadastrar(nickname="user_teste", email="test@test.com", senha=None)

    # Garante que nenhum cadastro foi realizado
    mock_repo.cadastro_user.assert_not_called()


def test_cadastrar_com_nickname_duplicado(mock_deps, mock_user):
    """Testa cadastro com nickname já existente no sistema"""
    mock_repo, mock_auth_controller = mock_deps

    # Simula que o email não existe (passa na primeira validação)
    mock_repo.verifica_user.return_value = None
    # Simula que existe usuário com esse nickname
    mock_repo.buscar_user_por_nickname.return_value = mock_user

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    # Deve lançar erro ao tentar cadastrar nickname duplicado
    with pytest.raises(ValueError, match="Nickname já cadastrado|Nickname já existe"):
        controller.cadastrar(
            nickname="novo_user",  # Mesmo nickname do mock_user
            email="outro@email.com",
            senha="senha123"
        )

    # Garante que o cadastro não foi finalizado
    mock_repo.cadastro_user.assert_not_called()


def test_cadastrar_com_dados_validos_mas_erro_no_repositorio(mock_deps):
    """Testa comportamento quando o repositório falha ao salvar"""
    mock_repo, mock_auth_controller = mock_deps

    # Simula que todas as validações passam
    mock_repo.verifica_user.return_value = None
    mock_auth_controller.hash_senha.return_value = "hash_gerado"
    # Simula erro ao tentar cadastrar no banco
    mock_repo.cadastro_user.side_effect = Exception("Erro ao conectar no banco de dados")

    controller = UserController(
        repository=mock_repo,
        auth_controller=mock_auth_controller
    )

    # Deve propagar a exceção do repositório
    with pytest.raises(Exception, match="Erro ao conectar no banco de dados"):
        controller.cadastrar(
            nickname="user_teste",
            email="test@test.com",
            senha="senha123"
        )

    # Verifica que tentou cadastrar
    mock_repo.cadastro_user.assert_called_once()