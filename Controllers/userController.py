from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/users", tags=["Users"])
fake_db = [] #repositorio exemplo temporario

@router.post("/cadastrar")
async def cadastrar(nickname: str, email: str, senha: str):
    user = {
        "nickname": nickname,
        "email": email,
        "senha_hash": senha,  # hash será tratado em outro módulo
        "data_criacao": datetime.now(),
        "first_data_login": None,
        "vetor_roles": False
    }
    fake_db.append(user)
    return {"message": "Usuário cadastrado com sucesso!", "user": user}

@router.get("/buscar/{nickname}")
async def buscar(nickname: str):
    for user in fake_db:
        if user["nickname"].lower() == nickname.lower():
            return user
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@router.put("/atualizar/{nickname}")
async def atualizar(nickname: str, novo_email: Optional[str] = None):
    for user in fake_db:
        if user["nickname"].lower() == nickname.lower():
            if novo_email:
                user["email"] = novo_email
            return {"message": "Usuário atualizado com sucesso!", "user": user}
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@router.get("/listar")
async def listar():
    return fake_db

@router.delete("/deletar/{nickname}")
async def deletar(nickname: str):
    for user in fake_db:
        if user["nickname"].lower() == nickname.lower():
            fake_db.remove(user)
            return {"message": "Usuário deletado com sucesso!"}
    raise HTTPException(status_code=404, detail="Usuário não encontrado")
