from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from src.Repository.repository import Repository
from src.Database.models import UserModel
from src.Database.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


def get_repo(db: Session = Depends(get_db)):
    return Repository(db)


# REMOVIDA A CLASSE UserController - Usamos funções diretas (Clean Architecture no FastAPI)

@router.post("/cadastrar")
async def cadastrar(nickname: str, email: str, senha: str, repo: Repository = Depends(get_repo)):
    # Note que usamos 'repo' (o argumento), não 'self.repo'
    if repo.verifica_user(email):
        raise HTTPException(status_code=400, detail="Usuário com este e-mail já existe")

    novo_user = UserModel(
        nickname=nickname,
        email=email,
        senha_hash=senha,
        vetor_roles=[]
    )

    repo.cadastro_user(novo_user)
    return {"message": "Usuário cadastrado com sucesso!", "user": novo_user}


@router.get("/buscar/{nickname}")
async def buscar(nickname: str, repo: Repository = Depends(get_repo)):
    user = repo.buscar_por_nickname(nickname)
    if user:
        return user
    raise HTTPException(status_code=404, detail="Usuário não encontrado")


@router.put("/atualizar/{nickname}")
async def atualizar(nickname: str, novo_email: Optional[str] = None, repo: Repository = Depends(get_repo)):
    user = repo.buscar_por_nickname(nickname)

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if novo_email:
        user.email = novo_email
        repo.alterar_user(user)

    return {"message": "Usuário atualizado com sucesso!", "user": user}


@router.get("/listar")
async def listar(repo: Repository = Depends(get_repo)):
    return repo.listar_users()


@router.delete("/deletar/{nickname}")
async def deletar(nickname: str, repo: Repository = Depends(get_repo)):
    user = repo.buscar_por_nickname(nickname)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    repo.remove_user(user.id)
    return {"message": "Usuário deletado com sucesso!"}