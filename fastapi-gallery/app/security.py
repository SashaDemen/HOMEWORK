import re
from pathlib import Path

SAFE_RE = re.compile(r'[^a-zA-Z0-9._-]+')

def safe_filename(name: str) -> str:
    name = name.strip().replace("\\","/").split("/")[-1]
    name = name.lower()
    name = SAFE_RE.sub("-", name)
    name = name.strip(".-_")
    if not name:
        name = "file"
    return name[:100]

def is_safe_path(base: Path, path: Path) -> bool:
    try:
        base = base.resolve()
        path = path.resolve()
        return str(path).startswith(str(base))
    except Exception:
        return False
