from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Optional
from src.Repository.repository import Repository
from src.Database.user import User
from sqlalchemy.orm import Session
from src.Database.models import UserModel
from src.Database.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

def get_repo(db: Session = Depends(get_db)):
    return Repository(db)

class UserController:
    def __init__(self):
        self.repo = Repository()

    @router.post("/cadastrar")
    async def cadastrar(self, nickname: str, email: str, senha: str, repo: Repository = Depends(get_repo)):
        if self.repo.verifica_user(email):
            raise HTTPException(status_code=400, detail="Usuário com este e-mail já existe")

        novo_user = User(
            id=None,
            nickname=nickname,
            email=email,
            senha_hash=senha,
            data_criacao=datetime.now(),
            first_data_login=None,
            vetor_roles=[]
        )

        repo.cadastro_user(novo_user)
        return {"message": "Usuário cadastrado com sucesso!", "user": novo_user}

    @router.get("/buscar/{nickname}")
    async def buscar(self, nickname: str, repo: Repository = Depends(get_repo)):
        user = repo.buscar_por_nickname(nickname)
        if user:
            return user
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    @router.put("/atualizar/{nickname}")
    async def atualizar(self, nickname: str, novo_email: Optional[str] = None):
        users = self.repo.listar_users()
        for user in users:
            if user.nickname.lower() == nickname.lower():
                if novo_email:
                    user.email = novo_email
                self.repo.alterar_user(user)
                return {"message": "Usuário atualizado com sucesso!", "user": user}
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    @router.get("/listar")
    async def listar(self):
        return self.repo.listar_users()

    @router.delete("/deletar/{nickname}")
    async def deletar(self, nickname: str):
        users = self.repo.listar_users()
        for user in users:
            if user.nickname.lower() == nickname.lower():
                self.repo.remove_users(user)
                return {"message": "Usuário deletado com sucesso!"}
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
