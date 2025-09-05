import os
from pathlib import Path

BASE_DIR = Path(os.environ.get("APP_BASE_DIR") or Path(__file__).resolve().parent.parent)

STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
PROCESSED_DIR = STORAGE_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"
OUTBOX_DIR = BASE_DIR / "outbox"  # псевдо-відправлені листи .eml

for d in [STORAGE_DIR, UPLOADS_DIR, PROCESSED_DIR, LOGS_DIR, OUTBOX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "app.log"
