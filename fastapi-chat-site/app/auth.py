import time
from typing import Optional, Dict
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from .settings import SECRET_KEY, JWT_ALGO, JWT_EXPIRE

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS: Dict[str, str] = {
    "alice": pwd.hash("Secret#123"),
    "bob": pwd.hash("Secret#123"),
}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_user(username: str, password: str) -> bool:
    h = USERS.get(username)
    return bool(h and pwd.verify(password, h))

def create_token(sub: str) -> str:
    now = int(time.time())
    exp = now + int(JWT_EXPIRE.total_seconds())
    return jwt.encode({"sub": sub, "iat": now, "exp": exp}, SECRET_KEY, algorithm=JWT_ALGO)

def decode_token(token: str) -> Optional[str]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGO]).get("sub")
    except Exception:
        return None
