from typing import Optional
from datetime import datetime


class Repository:

   # classe pra comunicar com o bd

    def __init__(self, db: Optional[object] = None):
        """
        #inicia o repositório
        O db futuramente será a sessão do banco de dados como vamos usar fastapi
        """
        self.db = db

    def cadastro_user(self, user):
        pass

    def verifica_user(self, email: str):
        pass

    def compara_user(self, email: str, senha: str):
        pass

    def alterar_user(self, user):
        pass
