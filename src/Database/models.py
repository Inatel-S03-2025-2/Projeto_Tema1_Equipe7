from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)

    data_login = Column(DateTime)
    data_criacao = Column(DateTime, server_default=func.now())

    vetor_roles = Column(JSON, nullable=False)
