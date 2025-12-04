from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
import os
import hashlib, jwt
from sqlalchemy.orm import Session
from src.Database.database import get_db
from src.Repository.repository import Repository

router = APIRouter(prefix="/auth", tags=["Auth"])

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise Exception("ERRO: SECRET_KEY não definida ao ambiente!")


# Função de dependência para pegar o repositório
def get_repo(db: Session = Depends(get_db)):
    return Repository(db)


class authController:

    @staticmethod
    def hash_senha(senha: str):
        """Retorna o hash SHA256 da senha."""
        return hashlib.sha256(senha.encode()).hexdigest()

    @staticmethod
    def verificar_senha(senha: str, hash_salvo: str):
        return authController.hash_senha(senha) == hash_salvo

    @staticmethod
    def verificar_email(email: str):
        return "@" in email and "." in email

    @staticmethod
    def gerar_token(email: str):
        payload = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verificar_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return {"email": payload["sub"], "valid": True}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido")


@router.post("/login")
async def login(email: str, senha: str, repo: Repository = Depends(get_repo)):
    # 1. Busca o usuário no banco pelo email
    user = repo.verifica_user(email)

    # 2. Se o usuário não existe, erro
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas (Usuário não encontrado)")

    # 3. Verifica se a senha bate com o hash do banco
    if not authController.verificar_senha(senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas (Senha incorreta)")

    # 4. Gera o token se tudo estiver certo
    token = authController.gerar_token(email)
    return {"token": token}