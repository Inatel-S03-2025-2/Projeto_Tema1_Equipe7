import pytest
from src.Repository.repository import Repository
from src.Database.models import UserModel
from datetime import datetime, timezone


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


@pytest.fixture
def repository(mock_db):
    return Repository(db=mock_db)


@pytest.fixture
def user_data():
    return {
        "nickname": "test_user",
        "email": "test@exemplo.com",
        "senha_hash": "hash_da_senha_123",
        "vetor_roles": ["user"]
    }


@pytest.fixture
def mock_user():
    user = UserModel(
        id=1,
        nickname="usuario_teste",
        email="usuario@exemplo.com",
        senha_hash="hash_simulado",
        vetor_roles=["user"]
    )
    return user


# --- TESTES DE SUCESSO ---

def test_cadastro_user_sucesso(repository, mock_db, user_data):
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    novo_user = UserModel(**user_data)
    resultado = repository.cadastro_user(novo_user)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    assert resultado is not None


def test_buscar_por_nickname_sucesso(repository, mock_db, mock_user):
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    resultado = repository.buscar_por_nickname("usuario_teste")

    assert resultado == mock_user


# --- TESTES DE ERRO ---

def test_cadastro_erro_banco(repository, mock_db, user_data):
    """Testa se uma exceção do banco é propagada corretamente"""
    # Simula erro ao commitar
    mock_db.commit.side_effect = Exception("Erro de Conexão SQL")

    novo_user = UserModel(**user_data)

    with pytest.raises(Exception) as excinfo:
        repository.cadastro_user(novo_user)

    assert "Erro de Conexão SQL" in str(excinfo.value)
    mock_db.add.assert_called_once()


def test_buscar_por_nickname_nao_encontrado(repository, mock_db):
    """Testa busca por nickname inexistente"""
    mock_db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.buscar_por_nickname("nao_existe")

    assert resultado is None


def test_verifica_user_nao_encontrado(repository, mock_db):
    """Testa verificação de email inexistente"""
    mock_db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.verifica_user("email@nada.com")

    assert resultado is None


def test_remove_user_nao_encontrado(repository, mock_db):
    """Testa remover um ID que não existe"""
    mock_db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.remove_user(999)

    assert resultado is False
    # Garante que não tentou deletar nada se não achou o usuário
    mock_db.delete.assert_not_called()