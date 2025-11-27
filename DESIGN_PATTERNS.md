# Design Patterns Aplicados no Projeto

Este documento descreve o padrão de projeto aplicado no sistema de gerenciamento de usuários.

## Padrão Utilizado: Repository Pattern

O projeto utiliza o **Repository Pattern** como design pattern arquitetural implementado.

---

## Repository Pattern

### O que é?

O Repository Pattern é um padrão de design que abstrai a camada de acesso a dados, criando uma interface entre a lógica de negócio e a camada de persistência (banco de dados). Ele atua como uma "coleção de objetos em memória", ocultando os detalhes de como os dados são armazenados e recuperados.

### Por que usamos?

1. **Separação de Responsabilidades**: Controllers não precisam conhecer detalhes do banco de dados
2. **Facilita Testes**: Podemos mockar o Repository sem precisar de um banco real
3. **Centralização**: Toda lógica de acesso a dados fica em um só lugar
4. **Manutenibilidade**: Se precisarmos mudar o banco (MySQL → PostgreSQL), alteramos apenas o Repository

---

## Implementação no Projeto

### Localização no Código

**Arquivo**: `src/Repository/repository.py`

```python
from sqlalchemy.orm import Session
from src.Database.models import User
from datetime import datetime


class Repository:
    """
    Repository Pattern: Abstrai todas as operações de banco de dados.

    Esta classe centraliza todo o acesso ao banco, permitindo que
    os Controllers trabalhem com objetos Python sem conhecer SQL.
    """

    def __init__(self, db: Session):
        """
        Construtor recebe a sessão de banco (db),
        que será usada para todas as operações SQL.
        """
        self.db = db

    def cadastro_user(self, new_user: User) -> User:
        """
        Insere um novo usuário no banco.

        Abstrai: INSERT INTO users (...) VALUES (...)
        """
        new_user.data_criacao = datetime.now()
        self.db.add(new_user)       # Marca para INSERT
        self.db.commit()            # Executa o INSERT
        self.db.refresh(new_user)   # Atualiza objeto com dados do banco
        return new_user

    def verifica_user(self, email: str) -> User | None:
        """
        Busca um usuário pelo email.

        Abstrai: SELECT * FROM users WHERE email = ?
        """
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def compara_user(self, email: str, senha_hash: str) -> bool:
        """
        Verifica se o email existe e a senha está correta.

        Abstrai: Lógica de autenticação com consulta ao banco
        """
        user = self.verifica_user(email)
        return user is not None and user.senha_hash == senha_hash

    def alterar_user(self, user_atualizado: User) -> User | None:
        """
        Atualiza os dados de um usuário já existente.

        Abstrai: UPDATE users SET ... WHERE id = ?
        """
        self.db.merge(user_atualizado)   # Realiza UPDATE
        self.db.commit()
        return user_atualizado

    def listar_users(self) -> list[User]:
        """
        Retorna todos os usuários cadastrados.

        Abstrai: SELECT * FROM users
        """
        return self.db.query(User).all()
```

---

## Como o Repository Aparece no Diagrama UML

### Diagrama de Classes

No diagrama UML de classes, o Repository aparece como:

```
┌─────────────────────────────────┐
│         Repository              │
├─────────────────────────────────┤
│ - db: Session                   │
├─────────────────────────────────┤
│ + cadastro_user():              │
│ + verifica_user():              │
│ + compara_user():               │
│ + alterar_user():               │
└─────────────────────────────────┘
```

### Relações com Outras Classes

```
┌──────────────────┐
│  UserController  │
└────────┬─────────┘
         │
         │ usa
         ↓
┌──────────────────┐
│   Repository     │ ← Padrão Repository
└────────┬─────────┘
         │
         │ acessa
         ↓
┌──────────────────┐
│    Database      │
│  (MySQL/ORM)     │
└──────────────────┘
```

**Fluxo de dados**:
1. **Controller** recebe requisição HTTP
2. **Controller** chama métodos do **Repository**
3. **Repository** executa operações SQL através do ORM
4. **Repository** retorna objetos Python para o **Controller**
5. **Controller** retorna resposta HTTP

---

## Exemplo Prático de Uso

```python
# userController.py - COM Repository Pattern

repo = Repository()  # Instância do Repository

@router.get("/users/{nickname}")
async def buscar(nickname: str):
    # Controller NÃO conhece detalhes do banco (BOM!)
    users = repo.listar_users()

    for user in users:
        if user.nickname.lower() == nickname.lower():
            return user

    raise HTTPException(404, "Usuário não encontrado")


@router.post("/users/cadastrar")
async def cadastrar(nickname: str, email: str, senha: str):
    # Usa método do Repository, sem conhecer SQL (BOM!)
    if repo.verifica_user(email):
        raise HTTPException(400, "Email já existe")

    novo_user = User(
        id=None,
        nickname=nickname,
        email=email,
        senha_hash=senha,
        data_criacao=datetime.now(),
        first_data_login=None,
        vetor_roles=False
    )

    repo.cadastro_user(novo_user)
    return {"message": "Usuário cadastrado!", "user": novo_user}
```

**Vantagens**:
- Controller não conhece SQL
- Código reutilizável (métodos do Repository)
- Fácil de testar (pode mockar o Repository)
- Mudanças no banco afetam apenas o Repository

---

## Benefícios do Repository Pattern no Projeto

### 1. Testabilidade

**Sem Repository** - Precisa de banco real:
```python
def test_buscar_usuario():
    # Precisa configurar banco de teste
    db = setup_test_database()

    # Insere dados de teste no banco real
    db.execute("INSERT INTO users ...")

    # Testa
    response = buscar_usuario("teste")
```

**Com Repository** - Mock simples:
```python
def test_buscar_usuario(mocker):
    # Mock do Repository
    mock_repo = mocker.Mock()
    mock_repo.verifica_user.return_value = User(...)

    # Testa sem banco de dados!
    response = buscar_usuario("teste")
```

### 2. Centralização

Todas as queries SQL estão em **um único lugar**: `repository.py`

### 3. Manutenibilidade

Se precisarmos trocar o banco de dados:

```python
# Antes: Alterar SQL em vários lugares diferentes

# Depois: Alterar APENAS o Repository
class Repository:
    def verifica_user(self, email: str):
        # Mudou de MySQL para PostgreSQL?
        # Apenas esta linha muda
        return self.db.query(User).filter(User.email == email).first()
```

---

## Estrutura de Arquivos com Repository Pattern

```
src/
├── Controllers/
│   ├── authController.py      # USA o Repository
│   └── userController.py      # USA o Repository
│
├── Repository/
│   └── repository.py          # IMPLEMENTA o Repository Pattern ←
│
├── Database/
│   ├── database.py            # Configuração do banco
│   ├── models.py              # Modelos SQLAlchemy
│   └── user.py                # Estrutura de dados
│
└── main.py
```

**Fluxo de Dependências**:
```
main.py
  ↓
Controllers (authController, userController)
  ↓
Repository (repository.py) ← Repository Pattern aqui!
  ↓
Database (models.py, database.py)
  ↓
MySQL
```

---

## Casos de Uso no Diagrama UML

### Caso de Uso: Cadastrar Usuário

```
Sequência de chamadas com Repository Pattern:

Usuario → POST /users/cadastrar → UserController
                                        ↓
                                  verifica_user(email)
                                        ↓
                                   Repository
                                        ↓
                                    Database
                                        ↓
                                  retorna: None
                                        ↓
                                  cadastro_user(novo_user)
                                        ↓
                                   Repository
                                        ↓
                                INSERT INTO users...
                                        ↓
                                 retorna: User salvo
                                        ↓
                                  UserController
                                        ↓
                            retorna: {"message": "Sucesso"}
```

### Caso de Uso: Login

```
Usuario → POST /auth/login → AuthController
                                    ↓
                              compara_user(email, senha)
                                    ↓
                               Repository
                                    ↓
                        SELECT * FROM users WHERE...
                                    ↓
                            retorna: True/False
                                    ↓
                              AuthController
                                    ↓
                     retorna: {"token": "..."} ou Erro 401
```

---

## Métodos do Repository e Suas Responsabilidades

| Método | Responsabilidade | SQL Abstrato |
|--------|------------------|--------------|
| `cadastro_user(User)` | Inserir novo usuário | `INSERT INTO users ...` |
| `verifica_user(email)` | Buscar por email | `SELECT * WHERE email = ?` |
| `compara_user(email, senha)` | Validar login | `SELECT * WHERE email = ? AND senha = ?` |
| `alterar_user(User)` | Atualizar usuário | `UPDATE users SET ... WHERE id = ?` |
| `listar_users()` | Listar todos | `SELECT * FROM users` |

---

## Resumo

### O que implementamos?

**Repository Pattern**

### Onde está implementado?

📁 `src/Repository/repository.py`

### Como aparece no diagrama UML?

A classe **Repository** com seus 4 métodos principais:
- `cadastro_user()`
- `verifica_user()`
- `compara_user()`
- `alterar_user()`

### Quem usa o Repository?

Os Controllers:
- `authController.py` - Para autenticação
- `userController.py` - Para CRUD de usuários

### Benefício principal?

**Separação clara entre lógica de negócio (Controllers) e acesso a dados (Repository)**

---

## Diagrama Completo da Arquitetura com Repository Pattern

```
┌──────────────────────────────────────────────┐
│           Cliente (HTTP Request)             │
└───────────────────┬──────────────────────────┘
                    │
                    ↓
┌──────────────────────────────────────────────┐
│              Controllers                     │
│  (authController, userController)            │
│                                              │
│  - Recebe requisições HTTP                   │
│  - Valida entrada                            │
│  - Chama métodos do Repository ←────────┐   │
│  - Retorna respostas HTTP                    │
└───────────────────┬──────────────────────────┘
                    │
                    │ usa
                    ↓
┌──────────────────────────────────────────────┐
│          Repository Pattern                  │
│        (repository.py)                       │
│                                              │
│  - Abstrai acesso ao banco                   │
│  - Centraliza queries SQL                    │
│  - Retorna objetos Python                    │
│                                              │
│  Métodos:                                    │
│  • cadastro_user()                           │
│  • verifica_user()                           │
│  • compara_user()                            │
│  • alterar_user()                            │
└───────────────────┬──────────────────────────┘
                    │
                    │ acessa
                    ↓
┌──────────────────────────────────────────────┐
│            Database Layer                    │
│     (SQLAlchemy ORM + MySQL)                 │
│                                              │
│  - Modelos (UserModel)                       │
│  - Conexão com banco                         │
│  - Execução de SQL                           │
└──────────────────────────────────────────────┘
```

---

**Última atualização**: Novembro 2025

**Design Pattern Aplicado**: Repository Pattern
**Localização**: `src/Repository/repository.py`
**Relacionamento no UML**: Repository ↔ Controllers ↔ Database
