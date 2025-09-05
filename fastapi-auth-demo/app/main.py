from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import Dict, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import secrets

# ==========================================
# дуже простий FastAPI застосунок для демо
# тут показую дві авторизації:
# 1) HTTP Basic (коли браузер показує віконечко логіна)
# 2) OAuth2 (password flow) з видачею токена через /token
#   - токен у мене "фейковий" (uuid), зберігаю в пам'яті додатку,
#     але працює як справжній для демонстрації :)
# ==========================================

app = FastAPI(title="Auth Demo (HTTPBasic + OAuth2)")

# -------------------------
# "База даних" користувачів
# (в реальному житті так НЕ робіть, беріть з БД і хешуйте паролі)
# -------------------------
USERS: Dict[str, str] = {
    "alice": "Secret#123",
    "bob": "qwerty123",
}

# тут тримаємо активні токени (token -> {"user":..., "exp":...})
TOKENS: Dict[str, Dict[str, object]] = {}

# налаштовую провайдерів безпеки
basic_security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # повідомляємо docs, де брати токен

# скільки живе токен (для прикладу 2 години)
TOKEN_TTL = timedelta(hours=2)


def verify_basic(credentials: HTTPBasicCredentials = Depends(basic_security)) -> str:
    """Перевіряє логін/пароль з HTTP Basic.
    Повертає username, якщо все норм, інакше кидає 401."""
    username = credentials.username
    password = credentials.password

    # використовуємо compare_digest щоб не палити часом (трохи безпечніше)
    real = USERS.get(username)
    if not real or not secrets.compare_digest(real, password):
        # кидаємо 401 + www-authenticate заголовок для браузера
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid basic auth",
            headers={"WWW-Authenticate": "Basic"}
        )
    return username


def create_token_for_user(username: str) -> str:
    """Створює простий токен (uuid) і кладе його в пам'ять з expiry."""
    token = uuid4().hex  # випадковий рядок
    TOKENS[token] = {"user": username, "exp": datetime.utcnow() + TOKEN_TTL}
    return token


def get_user_from_token(token: str = Depends(oauth2_scheme)) -> str:
    """Дістає користувача з Bearer-токена. Якщо токен поганий або прострочений — 401."""
    data = TOKENS.get(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
    if data["exp"] < datetime.utcnow():
        # протермінований токен видаляємо, щоб не смітило
        TOKENS.pop(token, None)
        raise HTTPException(status_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})
    return str(data["user"])


@app.get("/")
def root():
    # просто щоб щось було на головній
    return {"hello": "this is simple auth demo, see /docs"}


# ---------------- HTTP BASIC DEMO ----------------

@app.get("/basic/secret")
def read_basic_secret(user: str = Depends(verify_basic)):
    # сюди можна зайти тільки з коректним Basic
    return {"ok": True, "msg": f"hi {user}, this is a super secret via BASIC"}


# ---------------- OAUTH2 (PASSWORD FLOW) DEMО ----------------

@app.post("/token")
def issue_token(form: OAuth2PasswordRequestForm = Depends()):
    """Ендпойнт видачі токена.
    Приймає form-data: username, password (і ще scope, але ми його ігноруємо).
    Повертає JSON: { access_token, token_type } як прийнято в OAuth2.
    """
    # перевіряємо користувача по тій самій "базі"
    real = USERS.get(form.username)
    if not real or not secrets.compare_digest(real, form.password):
        # 400 саме тут, бо так прописано в стандартних прикладах FastAPI
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_token_for_user(form.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me")
def who_am_i(user: str = Depends(get_user_from_token)):
    # сюди потрапляють тільки з валідним Bearer токеном
    return {"user": user, "info": "this is your private data (kind of)"}


@app.get("/data")
def some_private_data(user: str = Depends(get_user_from_token)):
    # ще один приватний маршрут для прикладу
    return {"numbers": [1, 2, 3], "owner": user}


# маленький ендпоінт щоб подивитись скільки токенів
@app.get("/debug/tokens")
def debug_tokens():
    # у реальному світі такого не роблять, але для навчання хай буде
    return {"count": len(TOKENS)}
