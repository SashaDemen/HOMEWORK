from pathlib import Path
import os

BASE_DIR = Path(os.environ.get("APP_BASE_DIR") or Path(__file__).resolve().parent.parent)

STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
PROCESSED_DIR = STORAGE_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

for d in [STORAGE_DIR, UPLOADS_DIR, PROCESSED_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".jpg",".jpeg",".png"}
ALLOWED_CT = {"image/jpeg","image/png"}
MAX_FILE_SIZE_MB = 4
TARGET_MAX_SIZE = (1600,1600)
TARGET_FORMAT = "webp"
QUALITY = 80
