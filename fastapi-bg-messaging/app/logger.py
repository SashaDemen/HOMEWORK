import logging
from .settings import LOG_FILE

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
fh.setFormatter(fmt)
logger.addHandler(fh)

def log_action(action: str, user: dict):
    u = f"{user.get('email') or user.get('id') or 'anonymous'}"
    logger.info(f"ACTION={action} USER={u} DATA={user}")
