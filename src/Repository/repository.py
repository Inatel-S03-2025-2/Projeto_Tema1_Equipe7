from sqlalchemy.orm import Session
from src.Database.models import User
from datetime import datetime

class Repository:

    def __init__(self, db: Session):
        """
        Construtor recebe a sessão de banco (db),
        que será usada para todas as operações SQL.
        """
        self.db = db

    def cadastro_user(self, new_user: User) -> User:
        """
        Insere um novo usuário no banco.
        """
        new_user.data_criacao = datetime.now()
        self.db.add(new_user)       # Marca para INSERT
        self.db.commit()            # Executa o INSERT
        self.db.refresh(new_user)   # Atualiza objeto com dados do banco 
        return new_user

    def verifica_user(self, email: str) -> User | None:
        """
        Busca um usuário pelo email.
        Retorna o User ou None se não existir.
        """
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def compara_user(self, email: str, senha_hash: str) -> bool:
        """
        Verifica se o email existe e a senha está correta.
        """
        user = self.verifica_user(email)
        return user is not None and user.senha_hash == senha_hash

    def alterar_user(self, user_atualizado: User) -> User | None:
        """
        Atualiza os dados de um usuário já existente.
        """
        self.db.merge(user_atualizado)   # Realiza UPDATE
        self.db.commit()
        return user_atualizado

    def listar_users(self) -> list[User]:
        """
        Retorna todos os usuários cadastrados.
        """
        return self.db.query(User).all()

    def remove_users():
