from datetime import datetime, timezone
from typing import Callable, Iterable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="FastAPI with Custom Middleware")


class LoggingAndHeaderMiddleware(BaseHTTPMiddleware):
    """
    1) Логує метод, URL і час отримання запиту.
    2) Перевіряє наявність заголовка X-Custom-Header (для захищених маршрутів).
    Якщо заголовка немає — повертає 400 і НЕ передає запит далі.
    """

    def __init__(self, app: FastAPI, *, exclude_paths: Iterable[str] = ()):
        super().__init__(app)
        # Шляхи, для яких заголовок НЕ обов'язковий
        self.exclude_paths = set(exclude_paths)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1) Логування моменту отримання
        now = datetime.now(tz=timezone.utc).isoformat()
        print(f"[{now}] {request.method} {request.url}")

        # 2) Перевірка заголовка (за винятком exclude_paths)
        path = request.url.path
        if path not in self.exclude_paths:
            if "X-Custom-Header" not in request.headers:
                print(f" -> missing X-Custom-Header for {path}; return 400")
                return JSONResponse(
                    {"detail": "Missing required header: X-Custom-Header"},
                    status_code=400,
                )

        return await call_next(request)


# Підключаємо middleware з винятками
app.add_middleware(
    LoggingAndHeaderMiddleware,
    exclude_paths=("/docs", "/redoc", "/openapi.json", "/public"),
)


@app.get("/public")
def public():
    """Публічний маршрут, не вимагає X-Custom-Header."""
    return {"ok": True, "msg": "This is a public endpoint (no header required)."}


@app.get("/ping")
def ping():
    """Простий GET, вимагає X-Custom-Header."""
    return {"ok": True, "msg": "pong"}


@app.post("/echo")
async def echo(payload: dict):
    """POST, повертає тіло запиту."""
    return {"ok": True, "received": payload}


@app.get("/secure-info")
def secure_info():
    """Захищений маршрут для демонстрації 400 без заголовка."""
    return {"ok": True, "msg": "Top secret 🤫"}


@app.get("/")
def root():
    return {
        "info": "Custom middleware demo.",
        "docs": "/docs",
        "try": ["/public", "/ping", "/echo", "/secure-info"],
        "header_required": "X-Custom-Header for all except /public, /docs, /redoc, /openapi.json",
    }
