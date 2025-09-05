from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
JWT_ALGO = "HS256"
JWT_EXPIRE = timedelta(hours=6)

ALLOWED_ORIGINS = {
    "http://localhost",
    "http://127.0.0.1",
    "http://testserver",
}

MAX_MESSAGE_LEN = 1000
RATE_LIMIT_COUNT = 6
RATE_LIMIT_WINDOW_SEC = 4
