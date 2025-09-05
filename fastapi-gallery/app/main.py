from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
import uuid

from .settings import UPLOADS_DIR, PROCESSED_DIR, ALLOWED_EXT, ALLOWED_CT, MAX_FILE_SIZE_MB
from .security import safe_filename, is_safe_path
from .queue import queue
from .tasks import optimize_image
from .schemas import UploadResult, TaskOut
from .logger import log

app = FastAPI(title="Photo Gallery API")

def validate_and_save(f: UploadFile) -> Path:
    if f.content_type not in ALLOWED_CT:
        raise HTTPException(status_code=400, detail=f"unsupported type: {f.content_type}")
    raw = f.file.read()
    f.file.seek(0)
    if len(raw) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="file too large")
    name = safe_filename(f.filename or "image")
    ext = Path(name).suffix or ".bin"
    if ext.lower() not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="unsupported extension")
    uid = uuid.uuid4().hex[:8]
    final = UPLOADS_DIR / f"{uid}-{name}"
    if not is_safe_path(UPLOADS_DIR, final):
        raise HTTPException(status_code=400, detail="bad filename")
    with final.open("wb") as out:
        out.write(raw)
    try:
        import os
        os.chmod(final, 0o600)
    except Exception:
        pass
    return final

@app.post("/gallery/upload", response_model=UploadResult, status_code=202)
async def upload(files: List[UploadFile] = File(...)):
    saved = []
    for f in files:
        try:
            p = validate_and_save(f)
            saved.append(p)
            log("uploaded", {"file": str(p)})
        except HTTPException as e:
            log("rejected", {"file": f.filename, "reason": e.detail})
            raise
    task_ids = []
    items = []
    for p in saved:
        tid = queue.enqueue("optimize_image", optimize_image, str(p))
        task_ids.append(tid)
        items.append({"id": p.stem, "filename": p.name})
    return UploadResult(items=items, task_ids=task_ids)

@app.get("/tasks/{task_id}", response_model=TaskOut)
def task_status(task_id: str):
    t = queue.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="not found")
    return TaskOut(id=t.id, name=t.name, status=t.status, result=t.result, error=t.error)

@app.get("/tasks")
def tasks_list():
    return [{"id": t.id, "name": t.name, "status": t.status, "error": t.error} for t in queue.all()]

@app.get("/gallery/download/{name}")
def download(name: str):
    name = safe_filename(name)
    p = PROCESSED_DIR / name
    if not p.exists() or not is_safe_path(PROCESSED_DIR, p):
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(p)

@app.get("/health")
def health():
    return {"ok": True}
