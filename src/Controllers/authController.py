from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import hashlib, jwt

router = APIRouter(prefix="/auth", tags=["Auth"])

# trocar para variavel de ambiente, NAO PODE FICAR HARDCODE
SECRET_KEY = "chave_super_secreta"

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
async def login(email: str, senha: str):
    # Validar no repository
    if email == "teste@email.com" and senha == "123":
        token = authController.gerar_token(email)
        return {"token": token}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")