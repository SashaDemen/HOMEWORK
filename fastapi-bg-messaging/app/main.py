from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi import Body
from fastapi.responses import JSONResponse, FileResponse
from typing import List
from pathlib import Path
from .schemas import SendEmailIn, TaskOut, UploadOut
from .queue import queue
from .tasks import send_email_task, process_image_task
from .settings import UPLOADS_DIR
from .logger import log_action

app = FastAPI(title="Messaging API with Background Queue")

@app.post("/emails/send", response_model=TaskOut, status_code=202)
def send_email(data: SendEmailIn):
    log_action("email_request", data.user.model_dump())
    tid = queue.enqueue("send_email", send_email_task, data.user.model_dump(), data.subject, data.body)
    return TaskOut(id=tid, name="send_email", status="PENDING")

@app.post("/files/upload", response_model=UploadOut, status_code=202)
async def upload_files(files: List[UploadFile] = File(...)):
    task_ids: List[str] = []
    saved: List[Path] = []
    for f in files:
        dst = UPLOADS_DIR / f.filename
        with dst.open("wb") as out:
            out.write(await f.read())
        saved.append(dst)
    for p in saved:
        tid = queue.enqueue("process_image", process_image_task, str(p))
        task_ids.append(tid)
    log_action("files_uploaded", {"count": len(saved)})
    return UploadOut(task_ids=task_ids)

@app.get("/tasks/{task_id}", response_model=TaskOut)
def task_status(task_id: str):
    t = queue.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut(id=t.id, name=t.name, status=t.status, result=t.result, error=t.error)

@app.get("/tasks")
def tasks_list():
    return [
        {"id": t.id, "name": t.name, "status": t.status, "error": t.error}
        for t in queue.all()
    ]

@app.get("/health")
def health():
    return {"ok": True}
