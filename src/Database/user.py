from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    nickname: str
    email: str
    senha_hash: str
    first_data_login: datetime | None
    data_criacao: datetime
    vetor_roles: list[str]