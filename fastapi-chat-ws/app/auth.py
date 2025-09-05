import time
from typing import Optional, Dict
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from .settings import SECRET_KEY, JWT_ALGO, JWT_EXPIRE

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# demo users (username -> hashed password)
USERS: Dict[str, str] = {
    "alice": pwd_ctx.hash("Secret#123"),
    "bob": pwd_ctx.hash("Secret#123"),
}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_user(username: str, password: str) -> bool:
    hashed = USERS.get(username)
    return hashed and pwd_ctx.verify(password, hashed)

def create_token(sub: str) -> str:
    now = int(time.time())
    exp = now + int(JWT_EXPIRE.total_seconds())
    payload = {"sub": sub, "iat": now, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGO)

def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGO])
        return payload.get("sub")
    except Exception:
        return None
