from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
from src.Repository.repository import Repository
from src.Database.user import User

router = APIRouter(prefix="/users", tags=["Users"])
repo = Repository()

class userController:

    async def cadastrar(nickname: str, email: str, senha: str):
        # Verifica se o usuário já existe pelo email
        if repo.verifica_user(email):
            raise HTTPException(status_code=400, detail="Usuário com este e-mail já existe")

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
        return {"message": "Usuário cadastrado com sucesso!", "user": novo_user}

    @router.get("/buscar/{nickname}")
    async def buscar(nickname: str):
        users = repo.listar_users()
        for user in users:
            if user.nickname.lower() == nickname.lower():
                return user
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    @router.put("/atualizar/{nickname}")
    async def atualizar(nickname: str, novo_email: Optional[str] = None):
        users = repo.listar_users()
        for user in users:
            if user.nickname.lower() == nickname.lower():
                if novo_email:
                    user.email = novo_email
                repo.alterar_user(user)
                return {"message": "Usuário atualizado com sucesso!", "user": user}
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    @router.get("/listar")
    async def listar():
        return repo.listar_users()

    @router.delete("/deletar/{nickname}")
    async def deletar(nickname: str):
        users = repo.listar_users()
        for user in users:
            if user.nickname.lower() == nickname.lower():
                repo._fake_db.remove(user)
                return {"message": "Usuário deletado com sucesso!"}
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
