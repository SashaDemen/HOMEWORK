from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel
import re

from .settings import ALLOWED_ORIGINS
from .auth import verify_user, create_token, decode_token, TokenOut
from .manager import manager
from .security import sanitize_text

app = FastAPI(title="Realtime Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(ALLOWED_ORIGINS),
    allow_credentials=False,
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["Authorization","Content-Type"],
)

class LoginIn(BaseModel):
    username: str
    password: str

@app.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn):
    if not verify_user(data.username, data.password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return TokenOut(access_token=create_token(data.username))

@app.get("/sessions/active")
def sessions_active():
    return {"active_users": manager.active_users()}

def _get_token(ws: WebSocket) -> str | None:
    auth = ws.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ",1)[1]
    return ws.query_params.get("token")

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    origin = ws.headers.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        await ws.close(code=1008)
        return

    token = _get_token(ws)
    user = decode_token(token) if token else None
    if not user:
        await ws.close(code=1008)
        return

    await manager.connect(user, ws)
    try:
        while True:
            data = await ws.receive_json()
            msg = sanitize_text(str(data.get("message","")))
            if not msg:
                continue
            limiter = manager.limiter_for(ws)
            if not limiter.allow():
                await ws.send_json({"type":"error","message":"rate limit"})
                continue
            payload = {"type":"chat","from":user,"message":msg}
            await manager.broadcast(user, payload)
    except WebSocketDisconnect:
        await manager.disconnect(user, ws)
    except Exception:
        await manager.disconnect(user, ws)

# static UI
app.mount("/static", StaticFiles(directory=str((__file__[:-8] + "static").replace("__init__.py",""))), name="static")

@app.get("/")
def index():
    return FileResponse(str((__file__.replace("__init__.py","") + "static/index.html")))
