import pytest
from src.Repository.repository import Repository
from src.Database.user import User
from datetime import datetime, timezone


@pytest.fixture
def mock_db(mocker):
    """
    Cria um mock (simulação) da sessão do banco de dados.
    O mocker cria um objeto falso que simula o comportamento do banco real.
    """
    return mocker.Mock()


@pytest.fixture
def repository(mock_db):
    """
    Cria uma instância do Repository com o banco de dados mockado.
    Assim testamos o Repository sem precisar de um banco real.
    """
    return Repository(db=mock_db)


@pytest.fixture
def user_data():
    """
    Retorna um dicionário com dados de usuário para usar nos testes.
    É uma fixture reutilizável para evitar repetir os mesmos dados.
    """
    return {
        "nickname": "test_user",
        "email": "test@exemplo.com",
        "senha_hash": "hash_da_senha_123",
        "first_data_login": None,
        "data_criacao": datetime.now(timezone.utc),
        "vetor_roles": ["user"]
    }


@pytest.fixture
def mock_user():
    """
    Cria um objeto User completo para usar nos testes.
    Representa um usuário que já existe no banco de dados.
    """
    return User(
        id=1,
        nickname="usuario_teste",
        email="usuario@exemplo.com",
        senha_hash="$2b$12$hash_bcrypt_exemplo",
        first_data_login=None,
        data_criacao=datetime.now(timezone.utc),
        vetor_roles=["user"]
    )

def test_cadastro_user_sucesso(repository, mock_db, user_data):
    """
    Testa se o cadastro de usuário funciona corretamente.

    Cenário: Todos os dados são válidos e o banco aceita o cadastro
    Resultado esperado: Usuário é criado e retornado com ID
    """
    # Cria o usuário que será retornado pelo "banco"
    user_criado = User(**user_data, id=1)

    # Configura o mock: quando chamar add() não faz nada (apenas simula)
    mock_db.add.return_value = None
    # Quando chamar commit() também não faz nada (simula salvar no banco)
    mock_db.commit.return_value = None
    # Quando chamar refresh() simula que o banco retornou o ID
    mock_db.refresh.return_value = None

    # Executa o método que estamos testando
    resultado = repository.cadastro_user(user_data)

    # Verificações (assertions):
    # 1. O método add() foi chamado uma vez
    mock_db.add.assert_called_once()
    # 2. O método commit() foi chamado para salvar
    mock_db.commit.assert_called_once()
    # 3. O resultado não é None (usuário foi criado)
    assert resultado is not None


def test_cadastro_user_erro_ao_salvar(repository, mock_db, user_data):
    """
    Testa o comportamento quando o banco falha ao salvar.

    Cenário: O banco de dados retorna erro (ex: queda de conexão)
    Resultado esperado: A exceção é propagada e o rollback é chamado
    """
    # Configura o mock para lançar uma exceção ao fazer commit
    mock_db.commit.side_effect = Exception("Erro de conexão com banco")

    # Tenta cadastrar e espera que lance uma exceção
    with pytest.raises(Exception, match="Erro de conexão com banco"):
        repository.cadastro_user(user_data)

    # Verifica que tentou adicionar o usuário
    mock_db.add.assert_called_once()
    # Verifica que tentou fazer commit
    mock_db.commit.assert_called_once()

# TESTES DE VERIFICAÇÃO DE USUÁRIO (POR EMAIL)

def test_verifica_user_existe(repository, mock_db, mock_user):
    """
    Testa a busca de um usuário que existe no banco.

    Cenário: Usuário com o email fornecido existe
    Resultado esperado: Retorna o objeto User
    """
    # Configura o mock para simular uma query do SQLAlchemy
    # query().filter().first() é o padrão do SQLAlchemy
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Executa a busca
    resultado = repository.verifica_user(email="usuario@exemplo.com")

    # Verificações:
    # 1. Retornou o usuário correto
    assert resultado == mock_user
    # 2. O email está correto
    assert resultado.email == "usuario@exemplo.com"
    # 3. O método query foi chamado
    mock_db.query.assert_called_once()


def test_verifica_user_nao_existe(repository, mock_db):
    """
    Testa a busca de um usuário que não existe.

    Cenário: Nenhum usuário tem o email fornecido
    Resultado esperado: Retorna None
    """
    # Configura o mock para retornar None (não encontrado)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Executa a busca
    resultado = repository.verifica_user(email="naoexiste@exemplo.com")

    # Verificações:
    # 1. Retornou None
    assert resultado is None
    # 2. Tentou buscar no banco
    mock_db.query.assert_called_once()


def test_verifica_user_com_email_none(repository, mock_db):
    """
    Testa busca com email None ou vazio.

    Cenário: Email inválido é fornecido
    Resultado esperado: Retorna None ou lança exceção
    """
    # Configura mock para retornar None
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Testa com None
    resultado_none = repository.verifica_user(email=None)
    assert resultado_none is None

    # Testa com string vazia
    resultado_vazio = repository.verifica_user(email="")
    assert resultado_vazio is None

# TESTES DE BUSCA DE USUÁRIO POR ID

def test_buscar_user_por_id_sucesso(repository, mock_db, mock_user):
    """
    Testa a busca de usuário por ID quando o usuário existe.

    Cenário: ID fornecido corresponde a um usuário
    Resultado esperado: Retorna o usuário
    """
    # Configura mock: query().get() é usado para buscar por ID
    mock_db.query.return_value.get.return_value = mock_user

    # Executa a busca
    resultado = repository.buscar_user_por_id(user_id=1)

    # Verificações:
    assert resultado == mock_user
    assert resultado.id == 1
    mock_db.query.assert_called_once()


def test_buscar_user_por_id_nao_encontrado(repository, mock_db):
    """
    Testa busca por ID quando o usuário não existe.

    Cenário: ID não corresponde a nenhum usuário
    Resultado esperado: Retorna None
    """
    # Configura mock para retornar None
    mock_db.query.return_value.get.return_value = None

    # Executa a busca
    resultado = repository.buscar_user_por_id(user_id=999)

    # Verificações:
    assert resultado is None
    mock_db.query.assert_called_once()


def test_buscar_user_por_id_invalido(repository, mock_db):
    """
    Testa busca com IDs inválidos.

    Cenário: IDs inválidos (negativo, zero, None)
    Resultado esperado: Retorna None ou lança exceção
    """
    ids_invalidos = [-1, 0, None]

    for id_invalido in ids_invalidos:
        # Configura mock para retornar None
        mock_db.query.return_value.get.return_value = None

        # Tenta buscar com ID inválido
        resultado = repository.buscar_user_por_id(user_id=id_invalido)

        # Deve retornar None para IDs inválidos
        assert resultado is None

# TESTES DE ALTERAÇÃO DE USUÁRIO

def test_alterar_user_sucesso(repository, mock_db, mock_user):
    """
    Testa a alteração de dados de um usuário existente.

    Cenário: Usuário existe e dados são atualizados
    Resultado esperado: Usuário atualizado é retornado
    """
    # Dados para atualização
    dados_atualizacao = {
        "email": "novo_email@exemplo.com"
    }

    # Configura mock: buscar o usuário retorna o mock_user
    mock_db.query.return_value.get.return_value = mock_user
    mock_db.commit.return_value = None

    # Executa a alteração
    resultado = repository.alterar_user(user_id=1, dados=dados_atualizacao)

    # Verificações:
    # 1. Commit foi chamado para salvar as alterações
    mock_db.commit.assert_called_once()
    # 2. Resultado não é None
    assert resultado is not None


def test_alterar_user_nao_encontrado(repository, mock_db):
    """
    Testa tentativa de alterar usuário inexistente.

    Cenário: ID não corresponde a nenhum usuário
    Resultado esperado: Retorna None ou lança ValueError
    """
    dados_atualizacao = {"email": "novo@exemplo.com"}

    # Configura mock: usuário não existe
    mock_db.query.return_value.get.return_value = None

    # Tenta alterar usuário inexistente
    resultado = repository.alterar_user(user_id=999, dados=dados_atualizacao)

    # Verificações:
    # Não deve fazer commit se usuário não existe
    mock_db.commit.assert_not_called()
    # Deve retornar None
    assert resultado is None


# ============================================================================
# TESTES DE DELEÇÃO DE USUÁRIO
# ============================================================================

def test_deletar_user_sucesso(repository, mock_db, mock_user):
    """
    Testa a deleção de um usuário existente.

    Cenário: Usuário existe e é deletado com sucesso
    Resultado esperado: Retorna True
    """
    # Configura mock: usuário existe
    mock_db.query.return_value.get.return_value = mock_user
    mock_db.delete.return_value = None
    mock_db.commit.return_value = None

    # Executa a deleção
    resultado = repository.deletar_user(user_id=1)

    # Verificações:
    # 1. Delete foi chamado
    mock_db.delete.assert_called_once_with(mock_user)
    # 2. Commit foi chamado para confirmar a deleção
    mock_db.commit.assert_called_once()
    # 3. Retornou True indicando sucesso
    assert resultado == True


def test_deletar_user_nao_encontrado(repository, mock_db):
    """
    Testa tentativa de deletar usuário inexistente.

    Cenário: ID não corresponde a nenhum usuário
    Resultado esperado: Retorna False e não chama delete
    """
    # Configura mock: usuário não existe
    mock_db.query.return_value.get.return_value = None

    # Tenta deletar usuário inexistente
    resultado = repository.deletar_user(user_id=999)

    # Verificações:
    # 1. Delete NÃO foi chamado
    mock_db.delete.assert_not_called()
    # 2. Commit NÃO foi chamado
    mock_db.commit.assert_not_called()
    # 3. Retornou False indicando falha
    assert resultado == False


def test_deletar_user_erro_no_banco(repository, mock_db, mock_user):
    """
    Testa comportamento quando o banco falha ao deletar.

    Cenário: Erro ao executar delete no banco
    Resultado esperado: Exceção é propagada e rollback é chamado
    """
    # Configura mock: usuário existe mas commit falha
    mock_db.query.return_value.get.return_value = mock_user
    mock_db.delete.return_value = None
    mock_db.commit.side_effect = Exception("Erro ao deletar")

    # Tenta deletar e espera exceção
    with pytest.raises(Exception, match="Erro ao deletar"):
        repository.deletar_user(user_id=1)

    # Verificações:
    # 1. Delete foi chamado
    mock_db.delete.assert_called_once()
    # 2. Commit foi tentado
    mock_db.commit.assert_called_once()


# ============================================================================
# TESTES DE LISTAGEM DE USUÁRIOS
# ============================================================================

def test_listar_users_com_usuarios(repository, mock_db, mock_user):
    """
    Testa listagem quando existem usuários no banco.

    Cenário: Banco tem múltiplos usuários
    Resultado esperado: Retorna lista com todos os usuários
    """
    # Cria uma lista de usuários
    lista_usuarios = [mock_user, mock_user, mock_user]

    # Configura mock: query().all() retorna a lista
    mock_db.query.return_value.all.return_value = lista_usuarios

    # Executa a listagem
    resultado = repository.listar_users()

    # Verificações:
    # 1. Retornou uma lista
    assert isinstance(resultado, list)
    # 2. A lista tem 3 usuários
    assert len(resultado) == 3
    # 3. Query foi chamada
    mock_db.query.assert_called_once()


def test_listar_users_vazio(repository, mock_db):
    """
    Testa listagem quando não há usuários.

    Cenário: Banco não tem usuários cadastrados
    Resultado esperado: Retorna lista vazia
    """
    # Configura mock: retorna lista vazia
    mock_db.query.return_value.all.return_value = []

    # Executa a listagem
    resultado = repository.listar_users()

    # Verificações:
    # 1. Retornou uma lista
    assert isinstance(resultado, list)
    # 2. A lista está vazia
    assert len(resultado) == 0
    # 3. Query foi chamada
    mock_db.query.assert_called_once()


# ============================================================================
# TESTES DE BUSCA POR NICKNAME
# ============================================================================

def test_buscar_user_por_nickname_sucesso(repository, mock_db, mock_user):
    """
    Testa busca de usuário por nickname quando existe.

    Cenário: Nickname fornecido corresponde a um usuário
    Resultado esperado: Retorna o usuário
    """
    # Configura mock para retornar o usuário
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Executa a busca
    resultado = repository.buscar_user_por_nickname(nickname="usuario_teste")

    # Verificações:
    assert resultado == mock_user
    assert resultado.nickname == "usuario_teste"
    mock_db.query.assert_called_once()


def test_buscar_user_por_nickname_nao_encontrado(repository, mock_db):
    """
    Testa busca por nickname quando não existe.

    Cenário: Nickname não corresponde a nenhum usuário
    Resultado esperado: Retorna None
    """
    # Configura mock para retornar None
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Executa a busca
    resultado = repository.buscar_user_por_nickname(nickname="nao_existe")

    # Verificações:
    assert resultado is None
    mock_db.query.assert_called_once()
