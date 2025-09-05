from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import re

from .settings import ALLOWED_ORIGINS
from .auth import verify_user, create_token, decode_token, TokenOut
from .manager import manager
from .security import sanitize_text

app = FastAPI(title="FastAPI Chat with WebSockets & JWT")

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
    token = create_token(data.username)
    return TokenOut(access_token=token)

@app.get("/sessions/active")
def sessions_active():
    return {"active_users": manager.active_users()}

def get_token_from_request(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    m = re.match(r"Bearer\s+(.+)", auth)
    if m:
        return m.group(1)
    token = request.query_params.get("token")
    return token

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    origin = websocket.headers.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008)
        return

    token = get_token_from_request(websocket.scope.get("headers_wrapper") or websocket)  # fallback below

    # Fallback for starlette WebSocket: extract from headers or query
    if token is None:
        auth = websocket.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ",1)[1]
        else:
            token = websocket.query_params.get("token")

    user = decode_token(token) if token else None
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(user, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg = sanitize_text(str(data.get("message","")))
            if not msg:
                # ignore empty
                continue

            limiter = manager.limiter_for(websocket)
            if not limiter.allow():
                await websocket.send_json({"type":"error","message":"rate limit"})
                continue

            payload = {"type":"chat","from":user,"message":msg}
            await manager.broadcast(sender=user, data=payload)
    except WebSocketDisconnect:
        await manager.disconnect(user, websocket)
    except Exception:
        await manager.disconnect(user, websocket)
