from typing import Optional, List
from datetime import datetime
from src.Database import user  # ajuste o caminho conforme sua estrutura de pastas


class Repository:
    """Camada responsável pela comunicação com o banco de dados (simulada por enquanto)."""

    def __init__(self, db: Optional[object] = None):
        # No futuro `db` será a sessão de banco
        self.db = db
        self._fake_db: List[user] = []

    def cadastro_user(self, user: user) -> user:
        """Cadastra um novo usuário."""
        user.id = len(self._fake_db) + 1
        user.data_criacao = datetime.now()
        self._fake_db.append(user)
        return user

    def verifica_user(self, email: str) -> Optional[user]:
        """Busca usuário pelo e-mail."""
        return next((u for u in self._fake_db if u.email.lower() == email.lower()), None)

    def compara_user(self, email: str, senha_hash: str) -> bool:
        """Compara e-mail e senha (já em hash)."""
        user = self.verifica_user(email)
        return user is not None and user.senha_hash == senha_hash

    def alterar_user(self, user_atualizado: user) -> Optional[user]:
        """Atualiza os dados de um usuário existente."""
        for i, u in enumerate(self._fake_db):
            if u.id == user_atualizado.id:
                self._fake_db[i] = user_atualizado
                return user_atualizado
        return None

    def listar_users(self) -> list[user]:
        """Retorna todos os usuários cadastrados."""
        return self._fake_db
