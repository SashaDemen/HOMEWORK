import logging
from .settings import LOGS_DIR

LOG_FILE = LOGS_DIR / "gallery.log"

logger = logging.getLogger("gallery")
logger.setLevel(logging.INFO)

fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
fh.setFormatter(fmt)
logger.addHandler(fh)

def log(action: str, info: dict):
    logger.info(f"{action} {info}")
