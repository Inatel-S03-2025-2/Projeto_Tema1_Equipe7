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
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def verifica_user(self, email: str) -> User | None:
        """
        Busca um usuário pelo email.
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
        self.db.merge(user_atualizado)
        self.db.commit()
        return user_atualizado

    def listar_users(self) -> list[User]:
        """
        Retorna todos os usuários cadastrados.
        """
        return self.db.query(User).all()

    def remove_user(self, user_id: int) -> bool:
        """
        Remove um usuário pelo ID.

        Retorna:
            True  -> Usuário removido com sucesso
            False -> Usuário não encontrado
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True
