from pathlib import Path
from PIL import Image, ImageOps
from .settings import PROCESSED_DIR, TARGET_MAX_SIZE, TARGET_FORMAT, QUALITY
from .security import is_safe_path
from .logger import log

def optimize_image(src: str) -> str:
    p = Path(src)
    out = PROCESSED_DIR / (p.stem + "." + TARGET_FORMAT)
    if not is_safe_path(PROCESSED_DIR, out):
        raise ValueError("unsafe output path")
    with Image.open(p) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB","RGBA"):
            im = im.convert("RGB")
        im.thumbnail(TARGET_MAX_SIZE)
        params = {}
        if TARGET_FORMAT.lower() == "webp":
            params["quality"] = QUALITY
            params["method"] = 6
        im.save(out, format=TARGET_FORMAT.upper(), **params)
    log("optimized", {"src": str(p), "out": str(out)})
    return str(out)
