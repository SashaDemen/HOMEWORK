from pathlib import Path
from typing import Dict, Any, List
from PIL import Image
from .settings import OUTBOX_DIR, PROCESSED_DIR
from .logger import log_action

def send_email_task(user: Dict[str, Any], subject: str, body: str) -> str:
    log_action("email_send_start", user)
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{user.get('email','user')}_{subject.replace(' ','_')}.eml"
    path = OUTBOX_DIR / filename
    content = f"""From: no-reply@example.com
To: {user.get('email')}
Subject: {subject}

{body}
"""
    path.write_text(content, encoding="utf-8")
    log_action("email_send_done", user)
    return str(path)

def process_image_task(src_path: str, max_size: int = 1024) -> str:
    p = Path(src_path)
    out = PROCESSED_DIR / p.name
    with Image.open(p) as im:
        im.thumbnail((max_size, max_size))
        im.save(out)
    return str(out)
