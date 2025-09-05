# Realtime Chat (FastAPI + WebSocket)

## Що є
- UI: `/` (статичний HTML/JS/CSS).
- Сервер: FastAPI WebSocket `/ws`, логін `/auth/login` (JWT), активні сесії `/sessions/active`.
- Санітизація повідомлень і простий rate-limit.
- CORS для локальних origin.
- ASGI-конфіг приклад: `gunicorn_conf.py` (UvicornWorker).

## Запуск локально
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Відкрий http://127.0.0.1:8000
```

## Логін
Демо-користувачі: `alice` / `bob`, пароль: `Secret#123`.
UI робить запит до `/auth/login`, отримує JWT і відкриває WS-з'єднання.

## Продуктивність/Безпека (ASGI)
- Gunicorn + UvicornWorker:
```bash
gunicorn -c gunicorn_conf.py app.main:app
```
- TLS термінувати на Nginx/Traefik (wss).
- Перевірка Origin у WS (див. `settings.ALLOWED_ORIGINS`).
- Без cookie → мінімізує CSRF-ризик; додатково можна перевіряти `Sec-WebSocket-Protocol`.
- Для горизонтального масштабування додайте Redis pub/sub для широкомовлення між інстансами.

## Тести
```bash
pytest -q
```

## Структура
```
fastapi-chat-site/
├─ app/
│  ├─ main.py
│  ├─ auth.py
│  ├─ manager.py
│  ├─ security.py
│  ├─ settings.py
│  └─ static/
│     ├─ index.html
│     ├─ style.css
│     └─ app.js
├─ tests/
│  └─ test_chat.py
├─ gunicorn_conf.py
├─ requirements.txt
└─ README.md
```
